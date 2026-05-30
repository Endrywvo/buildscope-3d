# Resumo Executivo — Casa 3D

## O que o sistema faz

Demonstração de **acompanhamento visual de construção** usando uma casa 3D (Three.js) e planilha Excel com 15 módulos identificáveis.

## Como funciona

1. Planilha define status de cada módulo (MOD-001…MOD-015)
2. Playwright abre `casa_3d.html`
3. JavaScript aplica cores por status
4. Sistema captura PNG, monta páginas e gera books

## Como rodar

```bash
./scripts/setup.sh
source .venv/bin/activate
python app/terminal_app.py
```

## Arquivos principais

| Tipo | Caminho |
|------|---------|
| HTML 3D | `entrada/casa_3d.html` |
| Planilha | `entrada/controle_modulos_casa.xlsx` |
| PNG geral | `saida_casa_3d/geral/CASA_3D_COLORIDA.png` |
| App | `app/terminal_app.py` |

## Próximos passos

1. Adicionar mais módulos ou detalhes na casa 3D
2. Personalizar status/cores na planilha
3. Versionar com Git
4. Publicar demo estática do HTML

## Migração

Projeto industrial anterior movido para `_backup_refatoracao_casa_3d/` sem exclusão permanente.
