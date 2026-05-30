# Guia Rápido — Casa 3D

## 1. Instalação

```bash
./scripts/setup.sh
source .venv/bin/activate
```

## 2. Configuração

Arquivos em `entrada/`:

| Arquivo | Descrição |
|---------|-----------|
| `casa_3d.html` | Modelo 3D Three.js |
| `controle_modulos_casa.xlsx` | 15 módulos e status |

Regenerar:

```bash
python app/gerar_modelo_casa_html.py
```

## 3. Atualizar planilha

Edite `entrada/controle_modulos_casa.xlsx` (aba **Modulos**).

Valide:

```bash
python app/terminal_app.py   # opção 1
python app/gerar_controle_modulos.py
```

## 4. Casa 3D geral colorida

```bash
python app/terminal_app.py   # opção 2
# ou
python app/colorir_modulos_3d.py
```

Saída: `saida_casa_3d/geral/CASA_3D_COLORIDA.png`

## 5. Perímetro de módulos

Opção 3 — informe MOD-001 até MOD-005.

Saídas em `saida_casa_3d/perimetros/`.

## 6. Módulos pontuais

Opção 4 — ex: `MOD-003, MOD-009, MOD-014`

Saídas em `saida_casa_3d/pontuais/`.

## 7. Página individual

Opção 5 — ex: `MOD-009`

Saída: `saida_casa_3d/paginas_modulos/PAGINA_MOD-009.png`

## 8. Books

Opções 6 (completo) e 7 (por status).

Saídas em `saida_casa_3d/book/`.

## 9. Limpar cores

Opção 8 → `saida_casa_3d/geral/MODELO_LIMPO.png`

## 10. Solução de problemas

| Problema | Solução |
|----------|---------|
| Casa não carregou | `python app/gerar_modelo_casa_html.py` |
| Playwright | `playwright install chromium` |
| Módulo não encontrado | Use MOD-001 a MOD-015 |

```bash
./scripts/validar.sh
```

## 11. Estrutura das pastas

Ver [README.md](../README.md).
