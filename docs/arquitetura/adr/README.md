# Architecture Decision Records

Cada arquivo registra **uma** decisão: o contexto, as alternativas, a escolha e
o que ela custou. Decisão registrada não é revogada em silêncio — se mudar,
entra um ADR novo que substitui o anterior.

| ADR | Decisão | Status |
|-----|---------|--------|
| [0001](0001-dois-bancos-por-natureza-do-dado.md) | PostgreSQL para palestrante, MongoDB para avaliação | Aceita |
| [0002](0002-clean-architecture.md) | Clean Architecture com portas e adaptadores | Aceita |
| [0003](0003-imagem-fora-do-banco.md) | Imagem no armazenamento, nome no banco | Aceita |
| [0004](0004-migrations-alembic.md) | Schema por migrations, sem `create_all` | Aceita |
| [0005](0005-jwt-stateless.md) | JWT sem estado, escrita autenticada e leitura pública | Aceita |
| [0006](0006-estrategia-de-testes.md) | Pirâmide de testes com bancos falsos e job separado para os reais | Aceita |
