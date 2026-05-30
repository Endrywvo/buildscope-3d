#!/usr/bin/env python3
"""Gera planilha consolidada de acompanhamento dos módulos."""

import casa3d_common as cc

if __name__ == "__main__":
    path = cc.gerar_controle_modulos_acompanhamento()
    print(f"Planilha: {path}")
