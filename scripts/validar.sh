#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ERROS=0
source .venv/bin/activate 2>/dev/null || { echo "[ERRO] .venv ausente"; exit 1; }
for f in app/*.py; do python -m py_compile "$f" || ERROS=$((ERROS+1)); done
for f in entrada/casa_3d.html entrada/controle_modulos_casa.xlsx; do
  [[ -f "$f" ]] && echo "  OK: $f" || { echo "[ERRO] $f"; ERROS=$((ERROS+1)); }
done
python - <<'PY'
import sys
sys.path.insert(0,"app")
import casa3d_common as cc
df = cc.carregar_modulos_excel()
print(f"  Módulos na planilha: {len(df)}")
PY
[[ $ERROS -eq 0 ]] && echo "Validação OK" || exit 1
