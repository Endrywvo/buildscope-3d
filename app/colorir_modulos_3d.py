#!/usr/bin/env python3
"""Colore todos os módulos conforme status e gera PNG geral."""

from __future__ import annotations

import argparse
import time

import pandas as pd
from playwright.sync_api import sync_playwright

import casa3d_common as cc


def montar_payload(tabela) -> list[dict]:
    payload = []
    relatorio = []
    for _, row in tabela.iterrows():
        mod_id = row["id"]
        status = row["status"]
        info = cc.info_status(status)
        payload.append({"id": mod_id, "color": info["hex"]})
        relatorio.append({
            "modulo": mod_id,
            "status": cc.status_canonico(status),
            "cor_hex": info["hex"],
            "cor_nome": info["nome_cor"],
        })
    return payload, relatorio


def executar(args: argparse.Namespace) -> None:
    cc.preparar_diretorios_saida()
    cc.gerar_legenda_status_json()
    tabela = cc.carregar_modulos_excel()
    payload, relatorio = montar_payload(tabela)

    with cc.servidor_html() as url:
        with sync_playwright() as p:
            browser = cc.abrir_browser(p, headless=not args.no_headless)
            page = cc.abrir_pagina_casa(browser, url)
            time.sleep(args.espera)
            ready = cc.aguardar_casa(page)
            if not ready.get("ok"):
                browser.close()
                raise RuntimeError(ready.get("erro"))

            print(f"Aplicando cores em {len(payload)} módulos...")
            page.evaluate(cc.JS_PINTAR_MODULOS, payload)
            time.sleep(args.pos_pintura)
            page.screenshot(path=str(cc.PNG_COLORIDA), full_page=False)
            print(f"PNG: {cc.PNG_COLORIDA}")

            page.evaluate(cc.JS_RESTAURAR_MODELO)
            pd.DataFrame(relatorio).to_csv(
                cc.RELATORIO_COLORACAO, index=False, sep=";", encoding="utf-8-sig"
            )
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Colore módulos 3D e gera PNG")
    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--espera", type=int, default=3)
    parser.add_argument("--pos-pintura", type=float, default=1.0)
    executar(parser.parse_args())


if __name__ == "__main__":
    main()
