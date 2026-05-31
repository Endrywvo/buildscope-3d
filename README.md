# Casa 3D — Acompanhamento Visual de Módulos

Demonstração genérica de acompanhamento visual de construção usando uma **casa 3D em HTML** (Three.js) e planilha de controle de módulos.

---

## O que faz

- Lê planilha Excel com status de cada módulo da casa (MOD-001…MOD-015)
- Abre modelo 3D no navegador via Playwright
- Aplica cores por status nos módulos 3D
- Gera PNG geral, perímetros, módulos pontuais, páginas individuais e books PDF/XLSX
- Menu interativo no terminal — sem memorizar comandos

---

## Instalação

```bash
cd /Users/endryw/workspace/scripts-kw
chmod +x scripts/*.sh
./scripts/setup.sh
source .venv/bin/activate
```

---

## Uso rápido

```bash
# Gerar HTML + planilha (primeira vez)
python app/gerar_modelo_casa_html.py

# App interativo
python app/terminal_app.py
```

| Opção | Ação |
|-------|------|
| 1 | Analisar planilha de módulos |
| 2 | Gerar casa 3D geral colorida |
| 3 | Gerar perímetro (MOD-001 até MOD-005) |
| 4 | Gerar módulos pontuais |
| 5 | Gerar página de um módulo |
| 6 | Gerar book completo |
| 7 | Gerar book por status |
| 8 | Limpar cores do modelo |

### Linha de comando

```bash
python app/colorir_modulos_3d.py
python app/criar_catalogo_modulos.py --de MOD-001 --ate MOD-005
python app/gerar_controle_modulos.py
```

---

## Estrutura

```
scripts-kw/                    (preparado como casa-3d-demo)
├── app/
│   ├── casa3d_common.py
│   ├── terminal_app.py
│   ├── terminal_operacoes.py
│   ├── gerar_modelo_casa_html.py
│   ├── colorir_modulos_3d.py
│   ├── criar_catalogo_modulos.py
│   └── gerar_controle_modulos.py
├── entrada/
│   ├── casa_3d.html
│   └── controle_modulos_casa.xlsx
├── saida_casa_3d/
│   ├── geral/
│   ├── perimetros/
│   ├── pontuais/
│   ├── paginas_modulos/
│   ├── book/
│   ├── relatorios/
│   └── catalogo_modulos/
├── docs/
├── scripts/
└── requirements.txt
```

---

## Módulos da casa

| ID | Nome |
|----|------|
| MOD-001 | Fundação |
| MOD-002 | Piso |
| MOD-003 | Parede frontal |
| MOD-004 | Parede traseira |
| MOD-005 | Parede lateral esquerda |
| MOD-006 | Parede lateral direita |
| MOD-007 | Telhado esquerdo |
| MOD-008 | Telhado direito |
| MOD-009 | Porta |
| MOD-010 | Janela frontal |
| MOD-011 | Janela lateral |
| MOD-012 | Garagem |
| MOD-013 | Chaminé |
| MOD-014 | Varanda |
| MOD-015 | Jardim |

---

## Status e cores

| Status | Cor |
|--------|-----|
| NAO INICIADO | Cinza claro |
| PENDENTE | Branco |
| EM ANDAMENTO | Azul |
| CONCLUIDO | Verde |
| BLOQUEADO | Cinza escuro |
| INSPECIONAR | Vermelho |

---

## Documentação

- [docs/GUIA_RAPIDO.md](docs/GUIA_RAPIDO.md)
- [docs/FLUXO_OPERACIONAL.md](docs/FLUXO_OPERACIONAL.md)
- [docs/ESTRUTURA_MODULOS.md](docs/ESTRUTURA_MODULOS.md)
- [docs/RESUMO_EXECUTIVO.md](docs/RESUMO_EXECUTIVO.md)

---

## Dependências

```
pandas, openpyxl, playwright, pillow, reportlab
```

Validação: `./scripts/validar.sh`

---
