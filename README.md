# API de Palestrantes — CRUD com SQL + NoSQL

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)

API REST para gerenciamento de palestrantes e avaliações de palestras, usando
**dois bancos por natureza do dado**: PostgreSQL para o dado estruturado do
palestrante e MongoDB para as avaliações (documentos flexíveis).

## O que este projeto demonstra

- **Modelagem de dados e escolha de tecnologia**: quando usar relacional vs. documento.
- **CRUD completo** com upload de imagem (arquivo em disco, referência no banco).
- **Integração entre dois bancos** no mesmo fluxo de request.
- **Camadas bem separadas** (routers → repositories → models/schemas → db).
- **Testes automatizados** com pytest.

## Arquitetura

\`\`\`mermaid
flowchart LR
    Cliente -->|HTTP| API[FastAPI]
    API -->|SQLAlchemy| PG[(PostgreSQL<br/>palestrantes)]
    API -->|Motor| MG[(MongoDB<br/>avaliacoes)]
    API -->|arquivos| FS[static/uploads]
\`\`\`

**Por que dois bancos:** o palestrante tem estrutura fixa e exige integridade
(SKU do arquivo, campos obrigatórios) → **PostgreSQL**. As avaliações são
flexíveis, denormalizadas e de alto volume (autor, nota, comentário, tags) →
**MongoDB**. A imagem é binária: fica em disco, e o banco guarda só o nome do arquivo.

## Stack

Python 3.12 · FastAPI · SQLAlchemy · Motor · PostgreSQL 15 · MongoDB 7 · Docker · pytest

## Como rodar

Pré-requisitos: Docker e um ambiente Python 3.12.

\`\`\`bash
cp .env.example .env
make up        # sobe PostgreSQL + MongoDB em container
make install   # instala as dependências
make test      # roda os testes
make run       # API em http://localhost:8000/docs
\`\`\`

A documentação interativa (Swagger) fica em \`/docs\`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | \`/health\` | Health check |
| GET | \`/palestrantes\` | Lista palestrantes |
| POST | \`/palestrantes\` | Cria (multipart: dados + foto) |
| GET | \`/palestrantes/{id}\` | Detalhe |
| PUT | \`/palestrantes/{id}\` | Edita (troca a foto e apaga a antiga) |
| DELETE | \`/palestrantes/{id}\` | Remove (apaga a imagem junto) |
| POST | \`/avaliacoes\` | Cria avaliação (valida o palestrante no Postgres) |
| GET | \`/avaliacoes/{palestrante_id}\` | Lista avaliações do palestrante |

## Estrutura

\`\`\`
app/
  main.py            # app FastAPI, monta rotas e arquivos estáticos
  core/config.py     # configuração via .env
  db/                # conexões: postgres.py (SQLAlchemy), mongo.py (Motor)
  models/            # entidades relacionais
  schemas/           # contratos Pydantic
  repositories/      # acesso a dados (SQL e NoSQL)
  routers/           # endpoints HTTP
  services/upload.py # gravação/remoção de imagens
tests/               # pytest
\`\`\`

## Testes

\`\`\`bash
make test
\`\`\`

Os testes de CRUD rodam em SQLite em memória, sem depender do banco de produção.
