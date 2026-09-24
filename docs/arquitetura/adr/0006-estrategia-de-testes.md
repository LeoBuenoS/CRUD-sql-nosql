# ADR-0006 — Pirâmide de testes: falsos por padrão, bancos reais num job à parte

**Status:** Aceita · **Data:** 2026-09 · **Contexto TOGAF:** Fase D + Requisitos

## Contexto

Dois bancos e um armazenamento de arquivos podem tornar a suíte lenta e
dependente de ambiente — o caminho mais curto para ninguém rodar teste antes de
commitar. Por outro lado, testar *só* com falsos esconde o que é específico de
cada banco: `ILIKE`, `server_default`, o pipeline de agregação, as migrations.

## Decisão

Quatro níveis, cada um pagando um custo proporcional ao que prova:

| Nível | Pasta | Dependências | O que prova |
|-------|-------|--------------|-------------|
| Unidade (domínio) | `tests/unit/test_entidades.py` | nenhuma | Invariantes do negócio |
| Unidade (aplicação) | `tests/unit/test_casos_de_uso_*.py` | portas falsas | Orquestração e erros |
| Arquitetura | `tests/unit/test_arquitetura.py` | nenhuma | A regra de dependência do ADR-0002 |
| Integração (API) | `tests/integration/` | SQLite + Mongo falso | Contrato HTTP, status, autenticação |
| Integração (bancos) | `tests/db/` | PostgreSQL + MongoDB reais | O que é específico de cada banco |

`tests/db/` é marcado com `@pytest.mark.db` e **pula sozinho** quando
`TEST_POSTGRES_URL` / `TEST_MONGO_URI` não existem. No CI, um job dedicado sobe
os dois bancos como *services* e roda `pytest -m db`.

A cobertura mínima é verificada no CI (`--cov-fail-under=95`), não apenas
reportada: número de cobertura que ninguém bloqueia vira enfeite.

## Consequências

**A favor**

- `make test` roda a suíte inteira em segundos, sem Docker.
- A regra de negócio é testada sem simular HTTP nem banco.
- O que só o banco real prova continua sendo testado — num job separado.
- A arquitetura é verificada por teste, não por revisão manual.

**Contra**

- Os falsos podem divergir do comportamento real (foi por isso que `tests/db/`
  existe: a divergência fica coberta onde importa).
- Duas configurações de teste para manter.
- O job com bancos é mais lento e pode falhar por infraestrutura, não por código.

## Estado atual

111 testes rápidos + 9 contra bancos reais; cobertura de **98,8%**, mínimo
exigido de 95%.
