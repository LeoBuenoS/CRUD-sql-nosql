# ADR-0001 — Dois bancos, escolhidos pela natureza do dado

**Status:** Aceita · **Data:** 2026-08 · **Contexto TOGAF:** Fase C (Dados)

## Contexto

O sistema lida com dois dados de natureza bem diferente. O **palestrante** tem
estrutura fixa, campos obrigatórios e precisa de integridade: um cadastro pela
metade é um problema real para o organizador. A **avaliação** é o oposto:
formato flexível (tags hoje, talvez mídia amanhã), volume que só cresce,
tolerante a inconsistência momentânea, e quase sempre lida em bloco por
palestrante.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Só PostgreSQL, avaliações em `JSONB` | Funcionaria. Mas não demonstra o critério de escolha entre modelos, que é o ponto do projeto |
| Só MongoDB | Perderia integridade referencial e unicidade no cadastro, onde elas importam |
| **Dois bancos, por natureza do dado** | **Escolhida** |

## Decisão

PostgreSQL guarda palestrantes e usuários; MongoDB guarda avaliações. A relação
entre eles é uma referência lógica (`palestrante_id`), validada no caso de uso
`CriarAvaliacao` no momento da escrita.

## Consequências

**A favor**

- Cada dado no modelo que melhor o representa.
- A agregação de notas fica trivial e rápida no Mongo.
- O cadastro ganha unicidade, tipos e índices de verdade.

**Contra**

- Não existe foreign key entre os bancos: a integridade é responsabilidade da
  aplicação, e há uma janela em que um palestrante removido ainda aceita
  avaliação (lacuna L3).
- Duas infraestruturas para operar, monitorar e backupear.
- Avaliações órfãs após remoção (lacuna L2).

**Mitigação:** a validação cruzada mora num único lugar — o caso de uso — e é
coberta por teste unitário e de integração. Consistência forte, se vier a ser
necessária, entra via outbox pattern (roadmap, incremento 3).
