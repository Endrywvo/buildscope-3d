# 🏗️ BuildScope 3D

### Plataforma de Acompanhamento Visual para Modelos 3D Baseados em HTML

O **BuildScope 3D** é uma plataforma de visualização e acompanhamento de progresso em modelos tridimensionais, permitindo que elementos de um projeto sejam monitorados visualmente através de status, cores, relatórios e capturas automatizadas.

O projeto utiliza modelos 3D em HTML (Three.js), planilhas Excel para controle operacional e automação em Python para geração de imagens, páginas técnicas e books executivos.

---

# 🚀 Principais Funcionalidades

### 📊 Controle Visual

* Leitura automática de planilhas Excel
* Associação entre módulos e elementos do modelo 3D
* Colorização automática baseada em status
* Atualização visual em tempo real

### 🖼️ Geração de Imagens

* Captura geral do modelo
* Captura de módulos específicos
* Captura de perímetros
* Captura de vizinhança dos elementos
* Imagens técnicas para relatórios

### 📄 Relatórios

* Relatórios em Excel
* Relatórios em Markdown
* Books em PDF
* Páginas individuais por módulo

### 🖥️ Terminal Interativo

* Interface simples baseada em perguntas
* Não requer conhecimento dos comandos internos
* Operações executadas por menus

---

# 🎯 Objetivo

O BuildScope 3D foi criado para transformar modelos tridimensionais em ferramentas de acompanhamento visual.

A plataforma pode ser utilizada para:

* Construção civil
* Casas e edifícios
* Projetos arquitetônicos
* Estruturas metálicas
* Equipamentos industriais
* Linhas de produção
* Ambientes BIM simplificados
* Treinamentos técnicos
* Gêmeos digitais (Digital Twins)

O modelo de casa fornecido é apenas uma demonstração do funcionamento da plataforma.

---

# 🏠 Modelo Demonstrativo

O projeto acompanha uma casa 3D simples composta por módulos independentes.

### Módulos

| ID      | Descrição               |
| ------- | ----------------------- |
| MOD-001 | Fundação                |
| MOD-002 | Piso                    |
| MOD-003 | Parede Frontal          |
| MOD-004 | Parede Traseira         |
| MOD-005 | Parede Lateral Esquerda |
| MOD-006 | Parede Lateral Direita  |
| MOD-007 | Telhado Esquerdo        |
| MOD-008 | Telhado Direito         |
| MOD-009 | Porta                   |
| MOD-010 | Janela Frontal          |
| MOD-011 | Janela Lateral          |
| MOD-012 | Garagem                 |
| MOD-013 | Chaminé                 |
| MOD-014 | Varanda                 |
| MOD-015 | Jardim                  |

---

# 🎨 Status e Cores

| Status       | Cor          |
| ------------ | ------------ |
| NÃO INICIADO | Cinza Claro  |
| PENDENTE     | Branco       |
| EM ANDAMENTO | Azul         |
| CONCLUÍDO    | Verde        |
| BLOQUEADO    | Cinza Escuro |
| INSPECIONAR  | Vermelho     |

Essas cores são aplicadas diretamente nos objetos do modelo 3D durante a execução.

---

# 🛠️ Instalação

### Clonar o projeto

```bash
git clone https://github.com/seu-usuario/buildscope-3d.git

cd buildscope-3d
```

### Instalar dependências

```bash
chmod +x scripts/*.sh

./scripts/setup.sh
```

### Ativar ambiente virtual

```bash
source .venv/bin/activate
```

---

# ⚙️ Dependências

Principais bibliotecas utilizadas:

```text
pandas
openpyxl
playwright
pillow
reportlab
```

Instalação manual:

```bash
pip install -r requirements.txt

playwright install chromium
```

---

# 📁 Estrutura do Projeto

```text
buildscope-3d/
│
├── app/
│   ├── terminal_app.py
│   ├── terminal_operacoes.py
│   ├── casa3d_common.py
│   ├── gerar_modelo_casa_html.py
│   ├── colorir_modulos_3d.py
│   ├── criar_catalogo_modulos.py
│   └── gerar_controle_modulos.py
│
├── entrada/
│   ├── casa_3d.html
│   └── controle_modulos_casa.xlsx
│
├── saida_casa_3d/
│   ├── geral/
│   ├── perimetros/
│   ├── pontuais/
│   ├── paginas_modulos/
│   ├── catalogo_modulos/
│   ├── relatorios/
│   └── book/
│
├── docs/
│
├── scripts/
│
├── requirements.txt
│
└── README.md
```

---

# 🖥️ Utilização

## Interface Interativa

Execute:

```bash
python app/terminal_app.py
```

Menu disponível:

```text
1 - Analisar planilha de módulos
2 - Gerar casa 3D geral colorida
3 - Gerar perímetro de módulos
4 - Gerar módulos pontuais
5 - Gerar página de um módulo
6 - Gerar book completo
7 - Gerar book por status
8 - Limpar cores do modelo
0 - Sair
```

---

# 📷 Saídas Geradas

## Imagem Geral

```text
saida_casa_3d/geral/
```

Exemplo:

```text
CASA_3D_COLORIDA.png
```

---

## Perímetros

```text
saida_casa_3d/perimetros/
```

Exemplo:

```text
PERIMETRO_MOD-001_MOD-005.png
PERIMETRO_MOD-001_MOD-005.xlsx
PERIMETRO_MOD-001_MOD-005.md
```

---

## Módulos Pontuais

```text
saida_casa_3d/pontuais/
```

Exemplo:

```text
MODULOS_PONTUAIS_MOD-003_MOD-009_MOD-014.png
```

---

## Páginas Individuais

```text
saida_casa_3d/paginas_modulos/
```

Exemplo:

```text
PAGINA_MOD-009.png
```

---

## Books

```text
saida_casa_3d/book/
```

Exemplo:

```text
BOOK_COMPLETO_CASA_3D.pdf

BOOK_STATUS_CONCLUIDO.pdf
```

---

# 🔄 Utilizando Outros Projetos 3D

O BuildScope 3D foi projetado para permitir a substituição completa do modelo 3D.

Você não está limitado à casa de demonstração.

É possível utilizar:

* Casas
* Prédios
* Equipamentos
* Máquinas
* Ambientes industriais
* Linhas de produção
* Estruturas
* Gêmeos digitais

---

## Adicionando um Novo Modelo

### Passo 1

Adicionar o arquivo HTML:

```text
entrada/
```

Exemplo:

```text
entrada/meu_projeto_3d.html
```

---

### Passo 2

Criar ou atualizar a planilha:

```text
entrada/controle_modulos_casa.xlsx
```

ou

```text
entrada/controle_modulos_projeto.xlsx
```

---

### Passo 3

Disponibilizar os módulos via JavaScript:

```javascript
window.modulosProjeto = {
    "MOD-001": objeto1,
    "MOD-002": objeto2,
    "MOD-003": objeto3
}
```

Funções recomendadas:

```javascript
window.setModuloColor(id, color)

window.resetModuloColors()

window.focusModulo(id)

window.focusModulos(ids)
```

---

### Passo 4

Executar normalmente:

```bash
python app/terminal_app.py
```

Nenhuma alteração na lógica principal será necessária.

---

# 🗺️ Roadmap

Próximas versões planejadas:

* Importação automática de modelos GLTF
* Importação de arquivos GLB
* Integração IFC/BIM
* Dashboard Web
* Banco de Dados SQLite/PostgreSQL
* Multiusuário
* API REST
* Histórico de alterações
* Controle de revisões
* Exportação avançada de relatórios
* Integração com Power BI
* Integração com SharePoint
* Geração automática de indicadores

---

# 📚 Documentação

Consulte a pasta:

```text
docs/
```

Documentos disponíveis:

* GUIA_RAPIDO.md
* FLUXO_OPERACIONAL.md
* ESTRUTURA_MODULOS.md
* RESUMO_EXECUTIVO.md
* VALIDACAO_FINAL.md

---

# ✅ Validação

Executar:

```bash
./scripts/validar.sh
```

O script verifica:

* Estrutura das pastas
* Dependências
* Planilhas
* Modelo HTML
* Scripts Python
* Arquivos de saída

---

# 📄 Licença

Este projeto é disponibilizado para fins educacionais, demonstrações técnicas e desenvolvimento de soluções de acompanhamento visual baseadas em modelos 3D.

---

### BuildScope 3D

**Visual Progress Tracking Platform**
**Transformando modelos 3D em ferramentas de acompanhamento operacional.**
