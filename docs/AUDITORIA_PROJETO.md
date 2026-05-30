# Auditoria — Casa 3D Demo

**Data:** 2026-05-30  
**Projeto:** Casa 3D — Acompanhamento Visual de Módulos

## Scripts ativos

| Arquivo | Função | Status |
|---------|--------|--------|
| `casa3d_common.py` | Módulo central | ESSENCIAL |
| `terminal_app.py` | Menu interativo | ESSENCIAL |
| `terminal_operacoes.py` | Operações | ESSENCIAL |
| `gerar_modelo_casa_html.py` | HTML + planilha | ESSENCIAL |
| `colorir_modulos_3d.py` | PNG geral | UTILIZADO |
| `criar_catalogo_modulos.py` | Catálogo | UTILIZADO |
| `gerar_controle_modulos.py` | Planilha consolidada | UTILIZADO |

## Entrada

| Arquivo | Status |
|---------|--------|
| `entrada/casa_3d.html` | ESSENCIAL |
| `entrada/controle_modulos_casa.xlsx` | ESSENCIAL |

## Saída

| Pasta | Status |
|-------|--------|
| `saida_casa_3d/geral/` | ESSENCIAL |
| `saida_casa_3d/perimetros/` | UTILIZADO |
| `saida_casa_3d/pontuais/` | UTILIZADO |
| `saida_casa_3d/paginas_modulos/` | UTILIZADO |
| `saida_casa_3d/book/` | UTILIZADO |
| `saida_casa_3d/relatorios/` | UTILIZADO |
| `saida_casa_3d/catalogo_modulos/` | UTILIZADO |

## Backup

Projeto anterior em `_backup_refatoracao_casa_3d/` — OBSOLETO, preservado.

## Métricas

- 15 módulos na planilha
- 15 meshes no HTML
- Dependências: pandas, openpyxl, playwright, pillow, reportlab
