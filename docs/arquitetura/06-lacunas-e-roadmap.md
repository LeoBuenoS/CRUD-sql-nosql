# 06 — Análise de lacunas e roadmap (Fases E e F)

Honestidade sobre o que **não** está resolvido vale mais que um diagrama
bonito. Esta é a distância entre a arquitetura atual e uma que aguentaria
produção de verdade.

## Lacunas

| # | Lacuna | Risco | Esforço |
|---|--------|-------|---------|
| L1 | Um único perfil autenticado: qualquer usuário edita qualquer palestrante | Alto | Baixo |
| L2 | Avaliações ficam órfãs quando o palestrante é removido | Médio | Baixo |
| L3 | Escrita em dois bancos sem transação distribuída: a avaliação pode entrar no Mongo logo após o palestrante ser removido do Postgres | Médio | Alto |
| L4 | Uploads em disco local impedem escalar a API horizontalmente | Alto | Médio |
| L5 | Sem refresh token nem revogação — o JWT vale até expirar | Médio | Médio |
| L6 | Sem rate limiting no login (força bruta) | Alto | Baixo |
| L7 | Upload valida extensão, não o conteúdo do arquivo | Médio | Baixo |
| L8 | Sem observabilidade: log estruturado, métricas, tracing | Médio | Médio |
| L9 | `/health` não verifica os bancos — responde ok com o Postgres fora | Médio | Baixo |
| L10 | Sem paginação nas avaliações: palestrante popular devolve tudo | Médio | Baixo |
| L11 | Repositório comita por conta própria; falta Unit of Work | Baixo | Médio |
| L12 | Sem política de retenção/LGPD para comentários de terceiros | Médio | Médio |

## Roadmap

### Incremento 1 — segurança e consistência (o que mais dói primeiro)

- **L1**: papel (`admin` / `participante`) no usuário e verificação no caso de uso.
- **L6**: rate limiting no `POST /auth/token`.
- **L9**: `/health` com checagem real de PostgreSQL e MongoDB.
- **L2**: remover palestrante apaga as avaliações dele (caso de uso, não cascade).

### Incremento 2 — escala

- **L4**: adaptador `ArmazenamentoS3` implementando a mesma porta; a troca é
  uma linha no composition root.
- **L10**: paginação nas avaliações, com índice `(palestrante_id, criado_em)` no Mongo.
- **L8**: log estruturado com correlation id e métricas Prometheus.

### Incremento 3 — maturidade

- **L5**: refresh token com lista de revogação.
- **L11**: Unit of Work explícito, com o commit sob controle do caso de uso.
- **L3**: outbox pattern para a escrita cruzada entre os bancos.
- **L12**: política de retenção e anonimização dos comentários.

## Princípio para a evolução

Nenhum item acima exige reescrever o domínio. É o teste real da arquitetura:
S3, refresh token, papéis e Unit of Work entram como **adaptador novo ou regra
nova**, não como cirurgia no núcleo — que é exatamente o que a separação em
camadas foi feita para permitir.
