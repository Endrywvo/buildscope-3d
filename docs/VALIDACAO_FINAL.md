# Validação Final — Casa 3D

**Data:** 2026-05-30

## Scripts

| Script | Status |
|--------|--------|
| gerar_modelo_casa_html.py | OK |
| gerar_controle_modulos.py | OK |
| colorir_modulos_3d.py | OK |
| criar_catalogo_modulos.py | OK (MOD-001..MOD-005) |
| terminal_app.py | OK (opções 1,2,4,5,8) |

## Dados

- Módulos na planilha: **15**
- Módulos no HTML: **15**

## Saídas geradas

- `saida_casa_3d/geral/CASA_3D_COLORIDA.png`
- `saida_casa_3d/geral/MODELO_LIMPO.png`
- `saida_casa_3d/pontuais/MODULOS_PONTUAIS_MOD-003_MOD-009_MOD-014.*`
- `saida_casa_3d/paginas_modulos/PAGINA_MOD-009.png`
- `saida_casa_3d/catalogo_modulos/MOD-001..005.png`
- `saida_casa_3d/relatorios/ANALISE_PLANILHA.*`

## Dependências

pandas, openpyxl, playwright, pillow, reportlab

## Confirmação nominal

Código ativo (`app/`, `docs/`, `README.md`) sem referências ao projeto industrial anterior.
