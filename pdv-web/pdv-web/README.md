# PDV Web

Sistema de **ponto de venda** para pequenos comércios: cadastro de produtos, vendas por código de barras,
cálculo de troco, baixa automática de estoque e painel do dia.

Projeto Integrador Transdisciplinar em Engenharia de Software II.

![Tela de venda](docs/imagens/05-nova-venda.png)

| | |
|---|---|
| **Back-end** | Python 3.10+ · Flask · padrão **MVC** |
| **Front-end** | HTML5 · CSS3 · JavaScript (sem frameworks) |
| **Banco de dados** | PostgreSQL |
| **Testes** | pytest (back-end) · node:test (front-end), com 102 testes automatizados |

## Documentação por situação-problema

| Situação | Conteúdo | Onde |
|---|---|---|
| **1. Planejamento** | Escopo e requisitos | [docs/situacao-1/01-escopo-e-requisitos.md](docs/situacao-1/01-escopo-e-requisitos.md) |
| | UML: casos de uso, classes, sequência, atividades e estados | [docs/situacao-1/02-modelagem-uml.md](docs/situacao-1/02-modelagem-uml.md) |
| | IHC: princípios, navegação, mapa conceitual, protótipo e mensagens | [docs/situacao-1/03-ihc-interface.md](docs/situacao-1/03-ihc-interface.md) |
| | Banco: modelo conceitual, lógico normalizado e físico | [docs/situacao-1/04-projeto-banco-de-dados.md](docs/situacao-1/04-projeto-banco-de-dados.md) |
| | Dicionário de dados | [docs/situacao-1/05-dicionario-de-dados.md](docs/situacao-1/05-dicionario-de-dados.md) |
| | Script do banco (PostgreSQL) | [database/schema.sql](database/schema.sql) |
| **2. Desenvolvimento** | Arquitetura MVC, rotas e tratamento de erros | [docs/situacao-2/01-arquitetura-mvc.md](docs/situacao-2/01-arquitetura-mvc.md) |
| | Manual de uso | [docs/situacao-2/02-manual-de-uso.md](docs/situacao-2/02-manual-de-uso.md) |
| | Roteiro dos vídeos | [docs/situacao-2/03-roteiro-dos-videos.md](docs/situacao-2/03-roteiro-dos-videos.md) |
| | Código-fonte | [app/](app/) · [tests/](tests/) |
| **3. Testes e validação** | Plano e resultado dos testes (verificação) | [docs/situacao-3/01-plano-e-resultado-de-testes.md](docs/situacao-3/01-plano-e-resultado-de-testes.md) |
| | Formulário de avaliação para os testadores | [docs/situacao-3/02-formulario-de-avaliacao.md](docs/situacao-3/02-formulario-de-avaliacao.md) |
| | Relatório de validação com 5 usuários | [docs/situacao-3/03-relatorio-de-validacao.md](docs/situacao-3/03-relatorio-de-validacao.md) |

## Estrutura do repositório

```
pdv-web/
├── app/                  # aplicação Flask (MVC)
│   ├── models/           #   M: regras de negócio e banco
│   ├── templates/        #   V: páginas HTML
│   ├── static/           #   V: CSS e JavaScript
│   └── controllers/      #   C: rotas
├── database/             # schema.sql (PostgreSQL), schema_sqlite.sql (testes), seed.sql
├── tests/                # testes pytest e tests/js (node:test)
├── docs/
│   ├── situacao-1/       # planejamento, UML, IHC, banco
│   ├── situacao-2/       # arquitetura, manual, roteiro dos vídeos
│   ├── situacao-3/       # testes, formulário, relatório de validação
│   └── imagens/          # capturas de tela
├── requirements.txt
└── run.py
```

## Como executar

### 1. Instalar

```bash
git clone https://github.com/SEU-USUARIO/pdv-web.git
cd pdv-web
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar o banco

**Com PostgreSQL (recomendado):**

```bash
createdb pdv
# Windows (PowerShell):
$env:DATABASE_URL = "postgresql://postgres:SUA_SENHA@localhost:5432/pdv"
# Linux/Mac:
export DATABASE_URL="postgresql://postgres:SUA_SENHA@localhost:5432/pdv"

flask --app run init-db --exemplos
```

**Sem instalar nada (SQLite, só para experimentar):** pule a variável `DATABASE_URL` e rode apenas
`flask --app run init-db --exemplos`. Será criado o arquivo `pdv.db`.

> `init-db` **apaga e recria** as tabelas. A opção `--exemplos` insere 10 produtos de demonstração.

### 3. Rodar

```bash
python run.py
```

Abra **http://127.0.0.1:5000** no navegador.

## Testes

```bash
pytest -v                               # 93 testes do back-end (models, controllers, utilitários)
node --test tests/js/carrinho.test.js   # 9 testes do front-end (exige Node.js 18+)
```

## Hospedagem (para o professor e os testadores)

O sistema roda no **Render** (site) com o banco **PostgreSQL no Neon**. Os dois são gratuitos; o banco
gratuito do próprio Render expira em 30 dias, por isso o banco fica no Neon.

1. **Banco (Neon):** crie uma conta em [neon.com](https://neon.com), crie um projeto (região *São Paulo*,
   se houver, ou *US East*) e copie a *connection string* (`postgresql://...?sslmode=require`).
2. **Site (Render):** em [render.com](https://render.com), entre com o GitHub e clique em
   **New → Blueprint**, escolhendo este repositório. O arquivo [`render.yaml`](render.yaml) já traz tudo
   configurado; o Render só pede o valor de `DATABASE_URL`: cole a connection string do Neon.
3. Aguarde o deploy (2 a 4 minutos) e abra o endereço `https://webpdv-xxxx.onrender.com`.

Na primeira inicialização as tabelas e os 10 produtos de exemplo são criados automaticamente
(`init-db --se-vazio`); nas seguintes, nada é apagado.

> **Plano gratuito:** depois de 15 minutos sem acesso, o site "dorme" e o primeiro acesso seguinte demora
> cerca de 1 minuto para carregar. É normal; os acessos seguintes são rápidos.

## Autor

Tony · <!-- seu e-mail ou LinkedIn -->
