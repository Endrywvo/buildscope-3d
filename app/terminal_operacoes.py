"""Operações do terminal — Casa 3D."""

from __future__ import annotations

import math
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from PIL import Image, ImageDraw
from playwright.sync_api import Page, sync_playwright
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import casa3d_common as cc


def parse_modulos_lista(texto: str) -> list[str]:
    encontrados = cc.MODULO_RE.findall(texto.upper())
    if not encontrados:
        raise ValueError(f"Nenhum módulo válido em: {texto!r}")
    return [cc.normalizar_modulo(m) for m in encontrados]


def filtrar_intervalo(df: pd.DataFrame, de: str, ate: str) -> pd.DataFrame:
    de_n = cc.normalizar_modulo(de)
    ate_n = cc.normalizar_modulo(ate)
    nums = df["id"].str.extract(r"MOD-(\d+)", expand=False).astype(int)
    de_num = int(re.search(r"\d+", de_n).group())
    ate_num = int(re.search(r"\d+", ate_n).group())
    if de_num > ate_num:
        de_num, ate_num = ate_num, de_num
    return df[(nums >= de_num) & (nums <= ate_num)].copy()


def modulos_proximos(df: pd.DataFrame, mod_id: str) -> pd.DataFrame:
    mid = cc.normalizar_modulo(mod_id)
    row = df[df["id"] == mid]
    if row.empty:
        raise ValueError(f"Módulo não encontrado: {mid}")
    linha = row.iloc[0].get("linha_mapa")
    coluna = row.iloc[0].get("coluna_mapa")
    if pd.isna(linha) or pd.isna(coluna):
        return row.copy()
    linha, coluna = int(linha), int(coluna)
    mask = (
        (df["linha_mapa"].between(linha - 1, linha + 1))
        & (df["coluna_mapa"].between(coluna - 2, coluna + 2))
        & (df["id"] != mid)
    )
    return pd.concat([row, df[mask]], ignore_index=True)


def payload_cores(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {"id": row["id"], "color": cc.cor_hex_por_status(row["status"])}
        for _, row in df.iterrows()
    ]


def adicionar_rodape(img_path: Path, *, mod_id: str, status: str, nome: str = "") -> None:
    info = cc.info_status(status)
    rgb = tuple(info["rgb"])
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    rodape_h = 120
    canvas = Image.new("RGB", (w, h + rodape_h), "white")
    canvas.paste(img, (0, 0))
    draw = ImageDraw.Draw(canvas)
    fonte_id = cc.carregar_fonte(28, bold=True)
    fonte = cc.carregar_fonte(16)
    y0 = h
    draw.rectangle([0, y0, w, h + rodape_h], fill=(248, 248, 248), outline=(30, 30, 30))
    draw.rectangle([16, y0 + 16, 72, y0 + 72], fill=rgb, outline=(0, 0, 0), width=2)
    draw.text((88, y0 + 12), mod_id, fill=(0, 0, 0), font=fonte_id)
    titulo = nome or mod_id
    draw.text(
        (88, y0 + 48),
        f"{titulo}  |  {cc.status_canonico(status)}  |  {info['nome_cor']}",
        fill=(40, 40, 40),
        font=fonte,
    )
    draw.text((88, y0 + 78), cc.PROJETO_NOME, fill=(100, 100, 100), font=fonte)
    canvas.save(img_path, quality=95)


class ViewerSession:
    def __init__(self, *, headless: bool = True, espera: int = 3):
        self.headless = headless
        self.espera = espera
        self._pw = self._browser = self._page = self._ctx = None

    def __enter__(self) -> Page:
        self._ctx = cc.servidor_html()
        url = self._ctx.__enter__()
        self._pw = sync_playwright().start()
        self._browser = cc.abrir_browser(self._pw, headless=self.headless)
        self._page = cc.abrir_pagina_casa(self._browser, url)
        time.sleep(self.espera)
        ready = cc.aguardar_casa(self._page)
        if not ready.get("ok"):
            raise RuntimeError(ready.get("erro", "Casa 3D não carregou"))
        return self._page

    def __exit__(self, *args: Any) -> None:
        if self._page:
            try:
                self._page.evaluate(cc.JS_RESTAURAR_MODELO)
            except Exception:
                pass
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
        if self._ctx:
            self._ctx.__exit__(*args)


def com_viewer(callback: Callable[[Page], Any], *, headless: bool = True, espera: int = 3) -> Any:
    with ViewerSession(headless=headless, espera=espera) as page:
        return callback(page)


def capturar_com_cores(page: Page, df: pd.DataFrame, *, foco_ids: list[str], pos_zoom: float = 0.5) -> None:
    page.evaluate(
        cc.JS_PINTAR_E_FOCAR,
        {"itens": payload_cores(df), "modulo_ids": foco_ids, "espera_ms": int(pos_zoom * 1000)},
    )
    time.sleep(pos_zoom)


def restaurar_modelo(page: Page) -> None:
    page.evaluate(cc.JS_RESTAURAR_MODELO)
    time.sleep(0.3)


def analisar_planilha() -> dict[str, Any]:
    cc.preparar_diretorios_saida()
    tabela = cc.carregar_modulos_excel()
    total = len(tabela)
    por_status = tabela["status"].apply(cc.status_canonico).value_counts().to_dict()
    sem_status = tabela[tabela["status"].isna() | (tabela["status"].astype(str).str.strip() == "")]["id"].tolist()
    por_linha = tabela.groupby("linha_mapa").size().to_dict()
    por_coluna = tabela.groupby("coluna_mapa").size().to_dict()

    md = [
        "# Análise da planilha de módulos",
        "",
        f"**Arquivo:** `{cc.EXCEL_CONTROLE.name}`",
        f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- Total de módulos: **{total}**",
        f"- Sem status: **{len(sem_status)}**",
        "",
        "## Por status",
        "",
        "| Status | Qtd |",
        "|--------|-----|",
    ]
    for st, qtd in sorted(por_status.items(), key=lambda x: -x[1]):
        md.append(f"| {st} | {qtd} |")

    cc.ANALISE_PLANILHA_MD.write_text("\n".join(md), encoding="utf-8")
    with pd.ExcelWriter(cc.ANALISE_PLANILHA_XLSX, engine="openpyxl") as w:
        tabela.to_excel(w, sheet_name="MODULOS", index=False)
        pd.DataFrame([{"STATUS": k, "QTD": v} for k, v in por_status.items()]).to_excel(
            w, sheet_name="POR_STATUS", index=False
        )
    return {"total": total, "por_status": por_status, "sem_status": sem_status, "por_linha": por_linha, "por_coluna": por_coluna}


def gerar_casa_geral(page: Page, *, pos_pintura: float = 1.0) -> Path:
    cc.preparar_diretorios_saida()
    cc.gerar_legenda_status_json()
    tabela = cc.carregar_modulos_excel()
    payload = payload_cores(tabela)
    page.evaluate(cc.JS_PINTAR_MODULOS, payload)
    time.sleep(pos_pintura)
    page.screenshot(path=str(cc.PNG_COLORIDA), full_page=False)
    restaurar_modelo(page)
    return cc.PNG_COLORIDA


def operar_perimetro(page: Page, de: str, ate: str, *, pos_zoom: float = 0.5) -> dict[str, Any]:
    cc.preparar_diretorios_saida()
    tabela = cc.carregar_modulos_excel()
    df = filtrar_intervalo(tabela, de, ate)
    if df.empty:
        raise RuntimeError("Nenhum módulo no intervalo informado.")
    de_n, ate_n = cc.normalizar_modulo(de), cc.normalizar_modulo(ate)
    tag = f"{de_n}_{ate_n}"
    dir_img = cc.PERIMETROS_DIR / tag
    dir_img.mkdir(parents=True, exist_ok=True)
    registros = []
    for _, row in df.iterrows():
        mid = row["id"]
        capturar_com_cores(page, df, foco_ids=[mid], pos_zoom=pos_zoom)
        arquivo = dir_img / f"{mid}.png"
        page.screenshot(path=str(arquivo), full_page=False)
        adicionar_rodape(arquivo, mod_id=mid, status=row["status"], nome=str(row.get("nome_modulo", "")))
        registros.append({"modulo": mid, "status": row["status"], "arquivo": str(arquivo)})
    ids = df["id"].tolist()
    capturar_com_cores(page, df, foco_ids=ids, pos_zoom=pos_zoom)
    pagina = cc.PERIMETROS_DIR / f"PERIMETRO_{tag}.png"
    page.screenshot(path=str(pagina), full_page=False)
    _montar_grid(registros, pagina, titulo=f"Perímetro {de_n} — {ate_n}")
    xlsx = cc.PERIMETROS_DIR / f"PERIMETRO_{tag}.xlsx"
    md = cc.PERIMETROS_DIR / f"PERIMETRO_{tag}.md"
    pd.DataFrame(registros).to_excel(xlsx, index=False)
    md.write_text(f"# Perímetro {de_n} — {ate_n}\n\nMódulos: {len(registros)}\n", encoding="utf-8")
    restaurar_modelo(page)
    return {"registros": registros, "pagina": pagina}


def operar_modulos_pontuais(page: Page, modulos: list[str], *, pos_zoom: float = 0.5) -> dict[str, Any]:
    cc.preparar_diretorios_saida()
    tabela = cc.carregar_modulos_excel()
    mods_n = [cc.normalizar_modulo(m) for m in modulos]
    faltando = sorted(set(mods_n) - set(tabela["id"]))
    encontrados = [m for m in mods_n if m in set(tabela["id"])]
    if not encontrados:
        raise ValueError(f"Nenhum módulo encontrado: {', '.join(faltando)}")
    df = tabela[tabela["id"].isin(encontrados)].copy()
    registros, resultados = [], []
    for m in mods_n:
        if m in faltando:
            resultados.append(f"{m} = NÃO ENCONTRADO")
            continue
        row = df[df["id"] == m].iloc[0]
        info = cc.info_status(row["status"])
        resultados.append(f"{m} = {info['nome_cor'].lower()}")
    for _, row in df.iterrows():
        mid = row["id"]
        capturar_com_cores(page, df, foco_ids=[mid], pos_zoom=pos_zoom)
        arquivo = cc.PONTUAIS_DIR / f"{mid}.png"
        page.screenshot(path=str(arquivo), full_page=False)
        adicionar_rodape(arquivo, mod_id=mid, status=row["status"], nome=str(row.get("nome_modulo", "")))
        registros.append({"modulo": mid, "status": row["status"], "arquivo": str(arquivo)})
    tag = "_".join(encontrados)
    pagina = cc.PONTUAIS_DIR / f"MODULOS_PONTUAIS_{tag}.png"
    if registros:
        capturar_com_cores(page, df, foco_ids=[r["modulo"] for r in registros], pos_zoom=pos_zoom)
        page.screenshot(path=str(pagina), full_page=False)
        _montar_grid(registros, pagina, titulo=f"Módulos: {', '.join(encontrados)}")
    xlsx = cc.PONTUAIS_DIR / f"MODULOS_PONTUAIS_{tag}.xlsx"
    md = cc.PONTUAIS_DIR / f"MODULOS_PONTUAIS_{tag}.md"
    pd.DataFrame(registros).to_excel(xlsx, index=False)
    md.write_text("\n".join(["# Módulos pontuais", ""] + [f"- {r}" for r in resultados]), encoding="utf-8")
    restaurar_modelo(page)
    return {"registros": registros, "resultados": resultados, "faltando": faltando, "pagina": pagina}


def operar_pagina_modulo(page: Page, mod_id: str, *, pos_zoom: float = 0.5) -> Path:
    cc.preparar_diretorios_saida()
    mid = cc.normalizar_modulo(mod_id)
    tabela = cc.carregar_modulos_excel()
    row = tabela[tabela["id"] == mid]
    if row.empty:
        raise ValueError(f"Módulo não encontrado: {mid}")
    row = row.iloc[0]
    df_viz = modulos_proximos(tabela, mid)
    foto_prox = cc.PAGINAS_MODULOS_DIR / f"FOTO_PROXIMA_{mid}.png"
    capturar_com_cores(page, df_viz, foco_ids=[mid], pos_zoom=pos_zoom * 0.8)
    page.screenshot(path=str(foto_prox), full_page=False)
    foto_peri = cc.PAGINAS_MODULOS_DIR / f"FOTO_PERIMETRO_{mid}.png"
    capturar_com_cores(page, df_viz, foco_ids=df_viz["id"].tolist(), pos_zoom=pos_zoom)
    page.screenshot(path=str(foto_peri), full_page=False)
    pagina = cc.PAGINAS_MODULOS_DIR / f"PAGINA_{mid}.png"
    _montar_pagina_individual(mid, row, foto_prox, foto_peri, df_viz, pagina)
    restaurar_modelo(page)
    return pagina


def limpar_cores(page: Page) -> Path:
    cc.preparar_diretorios_saida()
    restaurar_modelo(page)
    page.screenshot(path=str(cc.PNG_MODELO_LIMPO), full_page=False)
    return cc.PNG_MODELO_LIMPO


def gerar_book(page: Page, *, status_filtro: str | None = None, limite: int | None = None, pos_zoom: float = 0.4) -> tuple[Path, Path]:
    cc.preparar_diretorios_saida()
    tabela = cc.carregar_modulos_excel()
    df = tabela.copy()
    if status_filtro:
        st = cc.status_canonico(status_filtro)
        df = df[df["status"].apply(cc.status_canonico) == st]
    if limite:
        df = df.head(limite)
    if df.empty:
        raise RuntimeError("Nenhum módulo para o book.")
    if status_filtro:
        slug = cc.normalizar_texto(status_filtro).replace(" ", "_")
        pdf = cc.BOOK_DIR / f"BOOK_STATUS_{slug}.pdf"
        xlsx = cc.BOOK_DIR / f"BOOK_STATUS_{slug}.xlsx"
    else:
        pdf = cc.BOOK_DIR / "BOOK_COMPLETO_CASA_3D.pdf"
        xlsx = cc.BOOK_DIR / "BOOK_COMPLETO_CASA_3D.xlsx"
    tmp = cc.BOOK_DIR / "_capturas"
    tmp.mkdir(parents=True, exist_ok=True)
    registros = []
    for _, row in df.iterrows():
        mid = row["id"]
        capturar_com_cores(page, df, foco_ids=[mid], pos_zoom=pos_zoom)
        arq = tmp / f"{mid}.png"
        page.screenshot(path=str(arq), full_page=False)
        adicionar_rodape(arq, mod_id=mid, status=row["status"], nome=str(row.get("nome_modulo", "")))
        registros.append({"modulo": mid, "status": row["status"], "arquivo": str(arq)})
    pd.DataFrame(registros).to_excel(xlsx, index=False)
    _gerar_book_pdf(pdf, registros, tabela)
    restaurar_modelo(page)
    return pdf, xlsx


def _montar_grid(registros: list, out: Path, *, titulo: str) -> None:
    if not registros:
        return
    fonte_t = cc.carregar_fonte(26, bold=True)
    fonte = cc.carregar_fonte(13)
    tw, th = 640, 440
    cols = min(2, len(registros))
    rows = math.ceil(len(registros) / cols)
    w = cols * tw + (cols + 1) * 32
    h = 80 + rows * (th + 70) + (rows + 1) * 32
    page = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(page)
    draw.text((32, 16), titulo, fill=(0, 0, 0), font=fonte_t)
    for i, reg in enumerate(registros):
        r, c = divmod(i, cols)
        x = 32 + c * (tw + 32)
        y = 72 + r * (th + 70 + 32)
        p = Path(reg["arquivo"])
        if p.exists():
            img = Image.open(p).convert("RGB")
            img.thumbnail((tw, th), Image.Resampling.LANCZOS)
            page.paste(img, (x, y))
        info = cc.info_status(reg["status"])
        key = reg.get("modulo", "")
        draw.text((x, y + th + 4), key, fill=(0, 0, 0), font=fonte)
        draw.text((x, y + th + 24), f"{cc.status_canonico(reg['status'])} — {info['nome_cor']}", fill=(60, 60, 60), font=fonte)
    page.save(out, quality=95)


def _montar_pagina_individual(mid, row, foto_prox, foto_peri, df_viz, out: Path) -> None:
    fonte_t = cc.carregar_fonte(30, bold=True)
    fonte = cc.carregar_fonte(15)
    fonte_sm = cc.carregar_fonte(12)
    info = cc.info_status(row["status"])
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w, h = 1600, 2000
    page = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(page)
    nome = str(row.get("nome_modulo", mid))
    draw.text((40, 24), f"{mid} — {nome}", fill=(0, 0, 0), font=fonte_t)
    draw.text((40, 70), f"Status: {cc.status_canonico(row['status'])}  |  Cor: {info['nome_cor']}", fill=(50, 50, 50), font=fonte)
    draw.text((40, 98), f"Grupo: {row.get('grupo','')}  |  Mapa: L{row.get('linha_mapa')} C{row.get('coluna_mapa')}", fill=(70, 70, 70), font=fonte_sm)
    draw.text((40, 120), f"Gerado em: {agora}", fill=(100, 100, 100), font=fonte_sm)
    y = 150
    for label, path in (("Zoom próximo", foto_prox), ("Vizinhos", foto_peri)):
        draw.text((40, y), label, fill=(0, 0, 0), font=fonte)
        y += 24
        if path.exists():
            img = Image.open(path).convert("RGB")
            img.thumbnail((720, 460), Image.Resampling.LANCZOS)
            page.paste(img, (40, y))
        y += 480
    draw.text((820, 150), "Módulos próximos", fill=(0, 0, 0), font=fonte)
    ty = 185
    for _, vr in df_viz.iterrows():
        vi = cc.info_status(vr["status"])
        draw.text((820, ty), f"{vr['id']}: {vi['nome_cor']}", fill=(40, 40, 40), font=fonte_sm)
        ty += 20
    draw.text((40, y + 10), "Legenda", fill=(0, 0, 0), font=fonte)
    ly = y + 40
    for chave, leg in cc.LEGENDA_STATUS.items():
        draw.text((40, ly), f"{chave}: {leg['nome_cor']}", fill=(60, 60, 60), font=fonte_sm)
        ly += 18
    page.save(out, quality=95)


def _gerar_book_pdf(pdf_path: Path, registros: list, tabela: pd.DataFrame) -> None:
    styles = getSampleStyleSheet()
    titulo_s = ParagraphStyle("t", parent=styles["Heading1"], alignment=TA_CENTER)
    corpo = ParagraphStyle("c", parent=styles["Normal"], fontSize=9)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4))
    story: list[Any] = [
        Spacer(1, 2 * cm),
        Paragraph("Book — Casa 3D", titulo_s),
        Paragraph(f"Gerado em: {datetime.now():%Y-%m-%d %H:%M}", corpo),
        PageBreak(),
    ]
    for i in range(0, len(registros), 2):
        par = registros[i : i + 2]
        cols = []
        for reg in par:
            p = Path(reg["arquivo"])
            cell = [RLImage(str(p), width=11 * cm, height=6.5 * cm), Paragraph(reg["modulo"], corpo)] if p.exists() else [Paragraph(reg["modulo"], corpo)]
            cols.append(cell)
        if len(cols) == 2:
            story.append(Table([[cols[0], cols[1]]], colWidths=[13 * cm, 13 * cm]))
        else:
            story.extend(cols[0])
    doc.build(story)
