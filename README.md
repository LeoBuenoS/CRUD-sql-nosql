# API de Palestrantes — CRUD com SQL + NoSQL

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248)
![Tests](https://img.shields.io/badge/tests-120%20passing-0A9EDC)
![Coverage](https://img.shields.io/badge/coverage-%E2%89%A595%25-brightgreen)
![Architecture](https://img.shields.io/badge/arquitetura-Clean%20Architecture-6E4AFF)
[![CI](https://github.com/LeoBuenoS/CRUD-sql-nosql/actions/workflows/ci.yml/badge.svg)](https://github.com/LeoBuenoS/CRUD-sql-nosql/actions/workflows/ci.yml)

API REST para gerenciamento de palestrantes e avaliações de palestras, usando
**dois bancos por natureza do dado**: PostgreSQL para o dado estruturado do
palestrante e MongoDB para as avaliações (documentos flexíveis).

## O que este projeto demonstra

- **Modelagem de dados e escolha de tecnologia**: quando usar relacional vs. documento.
- **Clean Architecture**: domínio sem framework, portas e adaptadores, com a regra
  de dependência verificada por teste automatizado.
- **Documentação de arquitetura no formato TOGAF** (ADM/BDAT) com ADRs — em
  [`docs/arquitetura/`](docs/arquitetura/).
- **CRUD completo** com upload de imagem (arquivo em disco, referência no banco).
- **Integração entre dois bancos** no mesmo fluxo de request.
- **Autenticação JWT** (bcrypt + OAuth2 password flow) protegendo a escrita.
- **Migrations versionadas** com Alembic (schema evolui sem `create_all`).
- **Agregação no MongoDB** para estatísticas das avaliações.
- **Busca e paginação** na listagem relacional.
- **Testes automatizados** com pytest e **CI** no GitHub Actions.
- **Containerização** da API (Dockerfile + docker compose).

## Arquitetura

```mermaid
flowchart TB
    subgraph I["interfaces/http"]
        R[routers · schemas · deps]
    end
    subgraph A["application"]
        UC[casos de uso]
    end
    subgraph D["domain"]
        EN[entidades · portas · erros]
    end
    subgraph INF["infrastructure"]
        PG[(PostgreSQL)] --- MG[(MongoDB)] --- FS[uploads] --- SEC[bcrypt · JWT]
    end
    I --> A --> D
    INF -.implementa as portas.-> D
```

A dependência aponta **sempre para dentro**: o domínio não importa FastAPI,
SQLAlchemy nem PyJWT — e há teste que falha se alguém furar essa regra
(`tests/unit/test_arquitetura.py`).

A documentação completa, no formato **TOGAF** (visão, negócio, dados, aplicação,
tecnologia, lacunas e ADRs), está em [`docs/arquitetura/`](docs/arquitetura/).

**Por que dois bancos:** o palestrante tem estrutura fixa e exige integridade
(SKU do arquivo, campos obrigatórios) → **PostgreSQL**. As avaliações são
flexíveis, denormalizadas e de alto volume (autor, nota, comentário, tags) →
**MongoDB**. A imagem é binária: fica em disco, e o banco guarda só o nome do arquivo.

## Stack

Python 3.12 · FastAPI · JWT · SQLAlchemy · Alembic · Motor · PostgreSQL 15 · MongoDB 7 · Docker · pytest

## Como rodar

Pré-requisitos: Docker e um ambiente Python 3.12.

```bash
cp .env.example .env
make up        # sobe PostgreSQL + MongoDB em container
make install   # instala as dependências
make migrate   # cria o schema (alembic upgrade head)
make test      # roda os testes
make run       # API em http://localhost:8000/docs
```

Ou suba tudo (API + bancos) em container — as migrations rodam no start:

```bash
make docker-up  # http://localhost:8000/docs
```

A documentação interativa (Swagger) fica em `/docs`.

## Endpoints

Escrita (POST/PUT/DELETE) exige `Authorization: Bearer <token>`; leitura é pública.

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/auth/registrar` | Cria usuário |
| POST | `/auth/token` | Login (OAuth2 password) → access token |
| GET | `/auth/eu` | Usuário do token 🔒 |
| GET | `/palestrantes` | Lista palestrantes (`?q=`, `?skip=`, `?limit=`) |
| POST | `/palestrantes` | Cria (multipart: dados + foto) 🔒 |
| GET | `/palestrantes/{id}` | Detalhe |
| PUT | `/palestrantes/{id}` | Edita (troca a foto e apaga a antiga) 🔒 |
| DELETE | `/palestrantes/{id}` | Remove (apaga a imagem junto) 🔒 |
| POST | `/avaliacoes` | Cria avaliação (valida o palestrante no Postgres) 🔒 |
| GET | `/avaliacoes/{palestrante_id}` | Lista avaliações do palestrante |
| GET | `/avaliacoes/{palestrante_id}/estatisticas` | Média, total e distribuição das notas |

## Autenticação

```bash
# 1. cria o usuário
curl -X POST localhost:8000/auth/registrar \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@exemplo.com","senha":"senha-super-secreta"}'

# 2. pega o token (form-urlencoded, padrão OAuth2)
curl -X POST localhost:8000/auth/token \
  -d 'username=dev@exemplo.com&password=senha-super-secreta'

# 3. usa nos endpoints de escrita
curl -X DELETE localhost:8000/palestrantes/1 -H "Authorization: Bearer $TOKEN"
```

A senha é guardada como hash **bcrypt** — o banco nunca vê o texto puro. O token
é um **JWT HS256** com `sub` (e-mail) e `exp`, assinado com `JWT_SECRET` (defina
no ambiente em produção). No `/docs`, o botão **Authorize** já funciona.

## Migrations

O schema do PostgreSQL é versionado com **Alembic** — a aplicação não cria
tabelas no boot.

```bash
make migrate                     # aplica as migrations pendentes
make migration m="nova coluna"   # gera uma a partir dos models
make downgrade                   # desfaz a última
```

`tests/test_migrations.py` roda o histórico completo em SQLite e compara o
schema resultante com os models: se alguém alterar um model e esquecer a
migration, o CI quebra.

As avaliações ficam no MongoDB e, por serem documentos flexíveis, não têm
schema versionado — a validação delas é feita pelos schemas Pydantic.

## Estrutura

```
app/
  main.py                  # monta a aplicação a partir das camadas
  domain/                  # o núcleo: não importa framework nenhum
    entities/              #   entidades imutáveis com as regras de negócio
    ports/                 #   contratos (Protocols) do que o domínio precisa
    errors.py              #   erros de negócio, sem HTTP
  application/use_cases/   # uma classe por operação de negócio
  infrastructure/          # adaptadores das portas
    db/ orm/ repositories/ #   PostgreSQL (SQLAlchemy) e MongoDB (Motor)
    security/ storage/     #   bcrypt, PyJWT, disco
    config.py              #   configuração via .env
  interfaces/http/         # entrega HTTP
    routers/ schemas/      #   endpoints e contratos de entrada/saída
    deps.py                #   composition root: amarra portas e adaptadores
    errors.py              #   erro de domínio -> status HTTP
migrations/                # Alembic (histórico do schema relacional)
docs/arquitetura/          # documentação TOGAF + ADRs
tests/
  unit/                    #   entidades, casos de uso e regra de dependência
  integration/             #   API completa, sem banco externo
  db/                      #   PostgreSQL e MongoDB reais (marcados `db`)
Dockerfile                 # imagem da API
.github/workflows/         # CI: qualidade + integração com bancos
```

## Testes

```bash
make test      # 120 testes, segundos, sem depender de banco externo
make cov       # o mesmo, com relatório de cobertura (mínimo 95%)
make test-db   # testes contra PostgreSQL e MongoDB de verdade
```

| Nível | O que prova | Dependências |
|-------|-------------|--------------|
| `tests/unit/` | Regras de negócio, casos de uso e a regra de dependência entre camadas | nenhuma |
| `tests/integration/` | Contrato HTTP, autenticação e as migrations | SQLite + Mongo falso |
| `tests/db/` | ILIKE, `server_default`, agregação e migrations no banco real | PostgreSQL + MongoDB |

Os testes de `tests/db/` se pulam sozinhos sem as variáveis de ambiente e rodam
num job dedicado do CI, com os bancos como *services*. O critério e os
trade-offs estão no [ADR-0006](docs/arquitetura/adr/0006-estrategia-de-testes.md).
