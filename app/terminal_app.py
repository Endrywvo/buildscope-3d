#!/usr/bin/env python3
"""App de terminal — Casa 3D (acompanhamento visual de módulos)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import casa3d_common as cc
from terminal_operacoes import (
    analisar_planilha,
    com_viewer,
    gerar_book,
    gerar_casa_geral,
    limpar_cores,
    operar_modulos_pontuais,
    operar_pagina_modulo,
    operar_perimetro,
    parse_modulos_lista,
)


class TerminalIO:
    def __init__(self) -> None:
        self.auto = os.environ.get("TERMINAL_AUTO", "").strip() in ("1", "true", "yes")
        self._fila: list[str] = []
        if self.auto and os.environ.get("TERMINAL_RESPOSTAS"):
            self._fila = [x.strip() for x in os.environ["TERMINAL_RESPOSTAS"].split("|") if x.strip()]

    def pergunta(self, texto: str, *, padrao: str = "") -> str:
        if self._fila:
            resp = self._fila.pop(0)
            print(f"{texto} {resp}")
            return resp
        resp = input(texto).strip()
        return resp or padrao

    def pausa(self) -> None:
        if not self.auto:
            input("\nPressione Enter para continuar...")

    def info(self, msg: str) -> None:
        print(msg)

    def erro(self, msg: str) -> None:
        print(f"\n[ERRO] {msg}")


def mostrar_menu() -> None:
    print(
        """
╔══════════════════════════════════════════════════════╗
║        CASA 3D — Acompanhamento Visual de Módulos    ║
╠══════════════════════════════════════════════════════╣
║  1 - Analisar planilha de módulos                    ║
║  2 - Gerar casa 3D geral colorida                    ║
║  3 - Gerar perímetro de módulos                      ║
║  4 - Gerar módulos pontuais                          ║
║  5 - Gerar página de um módulo                       ║
║  6 - Gerar book completo                             ║
║  7 - Gerar book por status                           ║
║  8 - Limpar cores do modelo                          ║
║  0 - Sair                                            ║
╚══════════════════════════════════════════════════════╝
"""
    )


def executar_com_viewer(io: TerminalIO, fn) -> None:
    headless = os.environ.get("TERMINAL_HEADLESS", "1") not in ("0", "false")
    io.info("\n  Abrindo casa 3D (Playwright)...")
    try:
        com_viewer(fn, headless=headless, espera=3)
    except Exception as e:
        io.erro(f"Falha: {e}\n  Verifique: playwright install chromium")


def main() -> None:
    io = TerminalIO()
    limite = int(os.environ.get("TERMINAL_LIMITE_BOOK", "0") or "0") or None

    io.info("=" * 54)
    io.info("  Casa 3D — Terminal Interativo")
    io.info("=" * 54)

    if not cc.HTML_CASA.exists() or not cc.EXCEL_CONTROLE.exists():
        io.info("\n  Gerando modelo e planilha...")
        from gerar_modelo_casa_html import gerar_html, gerar_planilha
        gerar_html()
        gerar_planilha()

    cc.preparar_diretorios_saida()

    while True:
        mostrar_menu()
        op = io.pergunta("Escolha uma opção: ")
        if op == "0":
            io.info("\nEncerrando.")
            break
        try:
            if op == "1":
                r = analisar_planilha()
                io.info(f"\n  Módulos: {r['total']}")
                for st, q in r["por_status"].items():
                    io.info(f"    {st}: {q}")
                io.info(f"\n  {cc.ANALISE_PLANILHA_XLSX}")

            elif op == "2":
                executar_com_viewer(io, lambda p: io.info(f"\n  PNG: {gerar_casa_geral(p)}"))

            elif op == "3":
                de = io.pergunta("Módulo inicial (Ex: MOD-001): ")
                ate = io.pergunta("Módulo final (Ex: MOD-005): ")
                def _op(p):
                    res = operar_perimetro(p, de, ate)
                    io.info(f"\n  Perímetro: {len(res['registros'])} módulos\n  {res['pagina']}")
                executar_com_viewer(io, _op)

            elif op == "4":
                txt = io.pergunta("Módulos separados por vírgula (Ex: MOD-003, MOD-009): ")
                mods = parse_modulos_lista(txt)
                def _op(p):
                    res = operar_modulos_pontuais(p, mods)
                    for linha in res["resultados"]:
                        io.info(f"    {linha}")
                    if res.get("pagina"):
                        io.info(f"  Página: {res['pagina']}")
                executar_com_viewer(io, _op)

            elif op == "5":
                mid = io.pergunta("Módulo (Ex: MOD-009): ")
                executar_com_viewer(io, lambda p: io.info(f"\n  Página: {operar_pagina_modulo(p, mid)}"))

            elif op == "6":
                def _op(p):
                    pdf, xlsx = gerar_book(p, limite=limite)
                    io.info(f"  PDF: {pdf}\n  XLSX: {xlsx}")
                executar_com_viewer(io, _op)

            elif op == "7":
                st = io.pergunta("Status (Ex: CONCLUIDO, EM ANDAMENTO): ")
                def _op(p):
                    pdf, xlsx = gerar_book(p, status_filtro=st, limite=limite)
                    io.info(f"  PDF: {pdf}\n  XLSX: {xlsx}")
                executar_com_viewer(io, _op)

            elif op == "8":
                executar_com_viewer(io, lambda p: io.info(f"\n  Limpo: {limpar_cores(p)}"))

            else:
                io.erro("Opção inválida.")
        except Exception as e:
            io.erro(str(e))
        io.pausa()


if __name__ == "__main__":
    main()
