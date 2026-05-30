# Fluxo Operacional — Casa 3D

```
Planilha Excel
      ↓
Módulos (MOD-001…MOD-015)
      ↓
Status → Cor
      ↓
casa_3d.html (Three.js)
      ↓
Playwright captura
      ↓
PNG / Book / Relatório
```

## Etapas

### 1. Planilha

`entrada/controle_modulos_casa.xlsx` — fonte de status por módulo.

### 2. Modelo 3D

`entrada/casa_3d.html` — 15 meshes identificáveis via `window.modulosCasa`.

API JavaScript:

- `setModuloColor(id, color)`
- `resetModuloColors()`
- `focusModulo(id)` / `focusModulos(ids)`
- `resetCamera()`

### 3. Colorização

Playwright executa JS no browser — cada operação pinta **somente** os módulos solicitados.

### 4. Captura

Screenshots PNG com rodapé informativo (PIL).

### 5. Página / Book

Composição visual (PIL) ou PDF (ReportLab).

## Modos

| Modo | Comando |
|------|---------|
| Terminal | `python app/terminal_app.py` |
| CLI geral | `python app/colorir_modulos_3d.py` |
| CLI catálogo | `python app/criar_catalogo_modulos.py --de MOD-001 --ate MOD-005` |

Cada execução é independente — cores restauradas ao final.
