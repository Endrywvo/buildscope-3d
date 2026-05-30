#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
python app/gerar_modelo_casa_html.py
python -c "import sys; sys.path.insert(0,'app'); import casa3d_common as cc; cc.preparar_diretorios_saida()"
echo "Instalação concluída. Execute: python app/terminal_app.py"
