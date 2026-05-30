#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .venv/bin/activate
pip install --upgrade -r requirements.txt
playwright install chromium
python app/gerar_controle_modulos.py
echo "Atualização concluída."
