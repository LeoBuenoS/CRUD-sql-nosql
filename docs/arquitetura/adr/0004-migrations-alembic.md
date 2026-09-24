# ADR-0004 — Schema por migrations, nunca por `create_all`

**Status:** Aceita · **Data:** 2026-09 · **Contexto TOGAF:** Fase C (Dados)

## Contexto

A aplicação criava as tabelas no boot com `Base.metadata.create_all()`. Isso
funciona na primeira execução e **só nela**: `create_all` cria o que falta, mas
não altera coluna, não cria índice novo, não renomeia nada. Na segunda mudança
de model, o banco em produção fica em silêncio, atrás do código.

## Decisão

O schema relacional é versionado com **Alembic**. A aplicação não cria tabela
nenhuma. O container roda `alembic upgrade head` antes de subir o servidor.

A URL do banco vem da configuração da aplicação (`.env`), não do `alembic.ini`,
para que exista **uma** fonte de verdade de conexão.

## Consequências

**A favor**

- O histórico do schema é legível e revisável no diff.
- Upgrade e downgrade determinísticos, iguais em qualquer ambiente.
- O índice de busca por nome virou uma migration própria, documentando *quando*
  e *por quê* apareceu.

**Contra**

- Mais um passo antes de rodar o projeto (`make migrate`).
- Autogenerate erra em alguns casos e exige revisão do arquivo gerado — foi o
  que aconteceu aqui: geradas contra SQLite, a migration de `usuarios` trouxe
  `CURRENT_TIMESTAMP` como literal e precisou virar `func.now()` para valer
  também no PostgreSQL.

## Como verificar

`tests/integration/test_migrations.py` roda o histórico completo, confere as
tabelas e os índices, testa o `downgrade base` e usa `compare_metadata` para
garantir que **não há diferença pendente** entre as migrations e os models.
Model alterado sem migration derruba o CI.

`tests/db/` roda as mesmas migrations contra um PostgreSQL real, cobrindo o que
o SQLite não é capaz de provar.
