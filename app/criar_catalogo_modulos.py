#!/usr/bin/env python3
"""Catálogo visual de módulos da casa 3D."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
from playwright.sync_api import sync_playwright

import casa3d_common as cc
from terminal_operacoes import adicionar_rodape, capturar_com_cores, filtrar_intervalo


def executar(args: argparse.Namespace) -> None:
    cc.preparar_diretorios_saida()
    cc.gerar_legenda_status_json()
    tabela = cc.carregar_modulos_excel()
    df = tabela.copy()
    if args.de and args.ate:
        df = filtrar_intervalo(df, args.de, args.ate)
    elif args.modulo:
        mid = cc.normalizar_modulo(args.modulo)
        df = df[df["id"] == mid]
    if args.status:
        st = cc.status_canonico(args.status)
        df = df[df["status"].apply(cc.status_canonico) == st]
    if args.limite:
        df = df.head(args.limite)
    if df.empty:
        raise RuntimeError("Nenhum módulo para capturar.")

    registros: list[dict[str, Any]] = []
    with cc.servidor_html() as url:
        with sync_playwright() as p:
            browser = cc.abrir_browser(p, headless=not args.no_headless)
            page = cc.abrir_pagina_casa(browser, url)
            time.sleep(args.espera)
            if not cc.aguardar_casa(page).get("ok"):
                browser.close()
                raise RuntimeError("Casa 3D não carregou")

            for i, (_, row) in enumerate(df.iterrows(), 1):
                mid = row["id"]
                print(f"  [{i}/{len(df)}] {mid}")
                capturar_com_cores(page, df, foco_ids=[mid], pos_zoom=args.pos_zoom)
                arquivo = cc.CATALOGO_MODULOS / f"{mid}.png"
                page.screenshot(path=str(arquivo), full_page=False)
                adicionar_rodape(arquivo, mod_id=mid, status=row["status"], nome=str(row.get("nome_modulo", "")))
                registros.append({"modulo": mid, "status": row["status"], "arquivo": str(arquivo)})

            page.evaluate(cc.JS_RESTAURAR_MODELO)
            browser.close()

    csv_path = cc.SAIDA / "catalogo_modulos.csv"
    pd.DataFrame(registros).to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")
    cc.gerar_controle_modulos_acompanhamento()
    print(f"Capturados: {len(registros)}")
    print(f"Catálogo: {cc.CATALOGO_MODULOS}")
    print(f"CSV: {csv_path}")


def main() -> None:
    p = argparse.ArgumentParser(description="Catálogo visual de módulos 3D")
    p.add_argument("--modulo", help="Ex: MOD-001")
    p.add_argument("--de", help="Módulo inicial")
    p.add_argument("--ate", help="Módulo final")
    p.add_argument("--status", help="Filtrar por status")
    p.add_argument("--limite", type=int)
    p.add_argument("--espera", type=int, default=3)
    p.add_argument("--pos-zoom", type=float, default=0.5)
    p.add_argument("--no-headless", action="store_true")
    executar(p.parse_args())


if __name__ == "__main__":
    main()
