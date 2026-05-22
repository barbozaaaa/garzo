# ✂️ Ana Ateliê — Sistema de Gestão Artesanal

Sistema web mobile-first desenvolvido para o projeto de extensão universitária **Conectados pela Comunidade**, que atua na Favela do Haiti (Vila Prudente, SP).

Criado para democratizar o acesso a dados e promover a inclusão digital através de uma ferramenta simples de gestão e Business Intelligence para um ateliê artesanal comunitário.

---

## 🖥️ Funcionalidades

| Tela | Descrição |
|---|---|
| **Ver Estoque** | Lista de materiais com foto, alertas de cor e filtro por categoria |
| **Adicionar Material** | Formulário simples com foto pelo celular |
| **Dar Baixa** | Registrar uso de material na produção |
| **Ver Produtos** | Calcula automaticamente quantas peças podem ser feitas com o estoque atual |
| **Alertas & Relatórios** | Alertas de estoque baixo + 3 gráficos de consumo (Chart.js) |

### Inteligência (Python)
- Estimativa de dias até o material acabar
- Material mais consumido
- **"Courino preto suficiente para mais 3 bolsas"** — cálculo por receita
- Gráfico de consumo semanal, por categoria e top materiais

---

## 🛠️ Stack Tecnológica

- **Backend:** Python + Flask
- **Banco de dados:** JSON (arquivo local, sem dependências externas)
- **Frontend:** HTML + CSS customizado (estética vintage artesanal)
- **Gráficos:** Chart.js (CDN)
- **Fontes:** Playfair Display + Crimson Text (Google Fonts)

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.8 ou superior

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Garzoju/Projeto---AnaAtelie.git
cd Projeto---AnaAtelie

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode o servidor
python app.py
```

Acesse em: **http://localhost:5000**

Para acessar pelo celular (mesma rede Wi-Fi): **http://SEU_IP_LOCAL:5000**

> Na primeira execução, o sistema cria automaticamente dados de exemplo para demonstração.

---

## 📁 Estrutura do Projeto

```
atelie-flask/
├── app.py              # Servidor Flask + todas as rotas
├── analytics.py        # Módulo de cálculos e BI em Python
├── requirements.txt
├── data/               # Banco de dados JSON (criado automaticamente)
│   ├── materiais.json
│   ├── movimentacoes.json
│   └── produtos.json
├── static/
│   └── uploads/        # Fotos dos materiais (upload pelo celular)
└── templates/
    ├── base.html       # Layout base (tipografia vintage, cores terracota)
    ├── home.html       # Tela inicial com 5 opções
    ├── estoque.html    # Lista de materiais
    ├── adicionar.html  # Formulário de novo material
    ├── baixa.html      # Dar baixa em material
    ├── produtos.html   # Produtos e cálculo de produção
    ├── novo_produto.html
    └── alertas.html    # Alertas + gráficos
```

---

## 🎨 Design

Interface com estética artesanal vintage:
- Fundo **creme quente** com gradiente sutil
- Fonte serifada **Playfair Display** nos títulos
- **Crimson Text** itálico nas legendas
- Cards com borda **terracota** e sombra artesanal
- Paleta: terracota · dourado · verde floresta · creme

---

## 📡 API — Rotas

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Tela inicial |
| GET | `/estoque` | Lista materiais (filtro por categoria e busca) |
| GET/POST | `/adicionar` | Adicionar novo material |
| GET/POST | `/baixa` | Dar baixa em material |
| POST | `/estoque/<id>/entrada` | Adicionar quantidade a material existente |
| POST | `/estoque/<id>/excluir` | Remover material |
| GET | `/produtos` | Ver produtos e produção possível |
| GET/POST | `/produtos/novo` | Cadastrar novo produto com receita |
| GET | `/alertas` | Dashboard de alertas e gráficos |

---

## 🤝 Projeto

**Conectados pela Comunidade** — Projeto de extensão universitária  
Favela do Haiti · Vila Prudente · São Paulo, SP

---

*Desenvolvido com carinho para democratizar o acesso à gestão e dados em comunidades.*
