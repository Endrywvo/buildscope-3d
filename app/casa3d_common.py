"""Utilitários compartilhados — Casa 3D (demonstração genérica)."""

from __future__ import annotations

import json
import re
import socket
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any, Iterator

import pandas as pd
from playwright.sync_api import Browser, Page, Playwright

BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
ENTRADA_DIR = BASE_DIR / "entrada"
SAIDA_DIR = BASE_DIR / "saida_casa_3d"
DOCS_DIR = BASE_DIR / "docs"

NOME_EXCEL = "controle_modulos_casa.xlsx"
ABA_EXCEL = "Modulos"
HTML_CASA = ENTRADA_DIR / "casa_3d.html"
EXCEL_CONTROLE = ENTRADA_DIR / NOME_EXCEL

SAIDA = SAIDA_DIR
SAIDA.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

PNG_COLORIDA = SAIDA / "geral" / "CASA_3D_COLORIDA.png"
PNG_MODELO_LIMPO = SAIDA / "geral" / "MODELO_LIMPO.png"
LEGENDA_JSON = SAIDA / "legenda_status.json"
DIAGNOSTICO_MD = SAIDA / "diagnostico_catalogo.md"
CONTROLE_ACOMPANHAMENTO_XLSX = SAIDA / "controle_modulos_acompanhamento.xlsx"
RELATORIO_COLORACAO = SAIDA / "relatorio_colorizacao.csv"

GERAL_DIR = SAIDA / "geral"
PERIMETROS_DIR = SAIDA / "perimetros"
PONTUAIS_DIR = SAIDA / "pontuais"
PAGINAS_MODULOS_DIR = SAIDA / "paginas_modulos"
BOOK_DIR = SAIDA / "book"
RELATORIOS_DIR = SAIDA / "relatorios"
CATALOGO_MODULOS = SAIDA / "catalogo_modulos"
CATALOGO_PAGINAS = SAIDA / "catalogo_paginas"
CATALOGO_PDF = SAIDA / "catalogo_pdf"
PDF_CATALOGO = CATALOGO_PDF / "CATALOGO_CASA_3D.pdf"

ANALISE_PLANILHA_XLSX = RELATORIOS_DIR / "ANALISE_PLANILHA.xlsx"
ANALISE_PLANILHA_MD = RELATORIOS_DIR / "ANALISE_PLANILHA.md"

PROJETO_NOME = "Casa 3D"
MODULOS_PADRAO = 15

VIEWPORT = {"width": 1600, "height": 1200}
BROWSER_ARGS = ["--enable-webgl", "--ignore-gpu-blocklist"]

LEGENDA_STATUS: dict[str, dict[str, Any]] = {
    "NAO INICIADO": {
        "rgb": [180, 180, 180],
        "hex": "#B4B4B4",
        "nome_cor": "CINZA CLARO",
        "descricao": "Módulo ainda não iniciado.",
    },
    "PENDENTE": {
        "rgb": [255, 255, 255],
        "hex": "#FFFFFF",
        "nome_cor": "BRANCO",
        "descricao": "Módulo pendente de definição ou início.",
    },
    "EM ANDAMENTO": {
        "rgb": [93, 173, 226],
        "hex": "#5DADE2",
        "nome_cor": "AZUL",
        "descricao": "Módulo em execução.",
    },
    "CONCLUIDO": {
        "rgb": [42, 157, 143],
        "hex": "#2A9D8F",
        "nome_cor": "VERDE",
        "descricao": "Módulo concluído.",
    },
    "BLOQUEADO": {
        "rgb": [80, 80, 80],
        "hex": "#505050",
        "nome_cor": "CINZA ESCURO",
        "descricao": "Módulo bloqueado — aguardando liberação.",
    },
    "INSPECIONAR": {
        "rgb": [231, 76, 60],
        "hex": "#E74C3C",
        "nome_cor": "VERMELHO",
        "descricao": "Módulo pendente de inspeção.",
    },
    "SEM INFORMACAO": {
        "rgb": [200, 200, 200],
        "hex": "#C8C8C8",
        "nome_cor": "CINZA",
        "descricao": "Status não informado na planilha.",
    },
}

MODULO_RE = re.compile(r"MOD-\d+", re.I)


def normalizar_texto(valor: Any) -> str:
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto)


def normalizar_modulo(valor: Any) -> str:
    texto = normalizar_texto(valor)
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    if texto.startswith("MOD") and not texto.startswith("MOD-"):
        numero = texto.replace("MOD", "")
        if numero.isdigit():
            return f"MOD-{int(numero):03d}"
    m = MODULO_RE.search(str(valor).upper())
    if m:
        num = int(re.search(r"\d+", m.group()).group())
        return f"MOD-{num:03d}"
    return texto


def status_canonico(status: str) -> str:
    status_norm = normalizar_texto(status)
    if not status_norm:
        return "SEM INFORMACAO"
    for chave in LEGENDA_STATUS:
        if normalizar_texto(chave) in status_norm or status_norm in normalizar_texto(chave):
            return chave
    if "CONCLU" in status_norm:
        return "CONCLUIDO"
    if "ANDAMENTO" in status_norm:
        return "EM ANDAMENTO"
    return "SEM INFORMACAO"


def info_status(status: str) -> dict[str, Any]:
    canon = status_canonico(status)
    base = LEGENDA_STATUS[canon].copy()
    base["status"] = canon
    return base


def cor_hex_por_status(status: str) -> str:
    return info_status(status)["hex"]


def cor_rgb_por_status(status: str) -> tuple[int, int, int]:
    return tuple(info_status(status)["rgb"])


def salvar_json(caminho: Path, dados: Any) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def gerar_legenda_status_json() -> Path:
    payload = {
        "projeto": PROJETO_NOME,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "status": [{"status": k, **v} for k, v in LEGENDA_STATUS.items()],
    }
    salvar_json(LEGENDA_JSON, payload)
    return LEGENDA_JSON


def carregar_modulos_excel() -> pd.DataFrame:
    if not EXCEL_CONTROLE.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {EXCEL_CONTROLE}")
    df = pd.read_excel(EXCEL_CONTROLE, sheet_name=ABA_EXCEL, engine="openpyxl")
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    col_id = "id_modulo" if "id_modulo" in df.columns else df.columns[0]
    df = df.rename(columns={col_id: "id"})
    df["id"] = df["id"].apply(normalizar_modulo)
    if "status" not in df.columns:
        df["status"] = "NAO INICIADO"
    df["status"] = df["status"].astype(str)
    return df


def preparar_diretorios_saida() -> None:
    for pasta in (
        GERAL_DIR,
        PERIMETROS_DIR,
        PONTUAIS_DIR,
        PAGINAS_MODULOS_DIR,
        BOOK_DIR,
        RELATORIOS_DIR,
        CATALOGO_MODULOS,
        CATALOGO_PAGINAS,
        CATALOGO_PDF,
    ):
        pasta.mkdir(parents=True, exist_ok=True)


def carregar_fonte(tamanho: int = 18, *, bold: bool = False):
    from PIL import ImageFont

    try:
        nome = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
        return ImageFont.truetype(nome, tamanho)
    except OSError:
        return ImageFont.load_default()


def _porta_livre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def iniciar_servidor(pasta: Path) -> tuple[ThreadingHTTPServer, int]:
    porta = _porta_livre()

    class _QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_args: Any) -> None:
            pass

    class Handler(_QuietHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(pasta), **kwargs)

    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor, porta


@contextmanager
def servidor_html(pasta: Path | None = None) -> Iterator[str]:
    pasta_servir = pasta or ENTRADA_DIR
    servidor, porta = iniciar_servidor(pasta_servir)
    url = f"http://127.0.0.1:{porta}/{HTML_CASA.name}"
    try:
        yield url
    finally:
        servidor.shutdown()


def abrir_browser(playwright: Playwright, *, headless: bool = True) -> Browser:
    return playwright.chromium.launch(headless=headless, args=BROWSER_ARGS)


def abrir_pagina_casa(
    browser: Browser,
    url: str,
    *,
    timeout_ms: int = 120_000,
    viewport: dict[str, int] | None = None,
) -> Page:
    vp = viewport or VIEWPORT
    page = browser.new_page(viewport=vp, device_scale_factor=1)
    page.goto(url, wait_until="networkidle", timeout=timeout_ms)
    return page


def aguardar_casa(page: Page, timeout_s: int = 30) -> dict[str, Any]:
    return page.evaluate(
        """
        async (timeoutS) => {
            const wait = ms => new Promise(r => setTimeout(r, ms));
            for (let i = 0; i < timeoutS * 10; i++) {
                if (window.captureReady && window.modulosCasa) {
                    return { ok: true, modulos: Object.keys(window.modulosCasa).length };
                }
                await wait(100);
            }
            return { ok: false, erro: "Casa 3D não carregou a tempo." };
        }
        """,
        timeout_s,
    )


JS_PINTAR_MODULOS = r"""
async (payload) => {
    await window.resetModuloColors();
    let pintados = 0;
    for (const item of payload) {
        if (item.id && item.color) {
            window.setModuloColor(item.id, item.color);
            pintados++;
        }
    }
    await new Promise(r => setTimeout(r, 400));
    return { ok: true, pintados };
}
"""


JS_PINTAR_E_FOCAR = r"""
async (params) => {
    await window.resetModuloColors();
    for (const item of (params.itens || [])) {
        if (item.id && item.color) window.setModuloColor(item.id, item.color);
    }
    const ids = params.modulo_ids || [];
    if (ids.length === 1) {
        window.focusModulo(ids[0]);
    } else if (ids.length > 1) {
        window.focusModulos(ids);
    }
    await new Promise(r => setTimeout(r, params.espera_ms || 500));
    return { ok: true, focados: ids.length };
}
"""


JS_RESTAURAR_MODELO = r"""
async () => {
    window.resetModuloColors();
    window.resetCamera();
    await new Promise(r => setTimeout(r, 300));
    return { ok: true };
}
"""


def gerar_controle_modulos_acompanhamento() -> Path:
    tabela = carregar_modulos_excel()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = []
    for _, row in tabela.iterrows():
        mod_id = row["id"]
        status = row.get("status", "NAO INICIADO")
        info = info_status(status)
        linhas.append({
            "ID_MODULO": mod_id,
            "NOME_MODULO": row.get("nome_modulo", ""),
            "GRUPO": row.get("grupo", ""),
            "LINHA_MAPA": row.get("linha_mapa"),
            "COLUNA_MAPA": row.get("coluna_mapa"),
            "STATUS_ATUAL": status_canonico(status),
            "COR_STATUS": info["nome_cor"],
            "DESCRICAO_STATUS": info["descricao"],
            "PROJETO": PROJETO_NOME,
            "OBSERVACAO": row.get("observacao", ""),
            "MANTER_NO_CONTROLE": row.get("manter_no_controle", "SIM"),
            "ULTIMA_ATUALIZACAO": agora,
        })
    df = pd.DataFrame(linhas)
    resumo = []
    for st, qtd in tabela["status"].apply(status_canonico).value_counts().items():
        info = info_status(st)
        resumo.append({"STATUS": st, "QUANTIDADE": qtd, "COR": info["nome_cor"]})
    with pd.ExcelWriter(CONTROLE_ACOMPANHAMENTO_XLSX, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="MODULOS_ACOMPANHAMENTO", index=False)
        pd.DataFrame(resumo).to_excel(w, sheet_name="RESUMO_STATUS", index=False)
    return CONTROLE_ACOMPANHAMENTO_XLSX
