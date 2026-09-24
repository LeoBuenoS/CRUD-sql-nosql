# ADR-0003 — A imagem fica no armazenamento; o banco guarda o nome

**Status:** Aceita · **Data:** 2026-08 · **Contexto TOGAF:** Fase C (Dados)

## Contexto

O palestrante tem uma foto. Binário em banco relacional infla backup, polui o
cache do servidor e faz `SELECT *` custar caro sem necessidade.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| `BYTEA` no PostgreSQL | Backup e replicação pagam por cada imagem; o banco vira CDN ruim |
| GridFS no MongoDB | Resolve o tamanho, mas acopla a imagem ao banco de avaliações, que nada tem a ver com ela |
| Objeto em S3 desde já | Melhor destino, mas exige credencial e serviço externo num projeto que precisa subir com um comando |
| **Arquivo no armazenamento local + nome no banco** | **Escolhida**, atrás de uma porta que permite trocar por S3 depois |

## Decisão

O upload é gravado pelo adaptador `ArmazenamentoLocal` com nome gerado por
UUID; o banco guarda apenas esse nome. A API monta a URL pública na resposta.
O contrato está na porta `ArmazenamentoDeArquivos`.

O nome enviado pelo cliente é **descartado** — só a extensão é aproveitada,
depois de validada contra uma lista de imagens permitidas. Isso elimina path
traversal e colisão de nomes.

## Consequências

**A favor**

- Banco enxuto; backup rápido.
- Servir imagem é trabalho de arquivo estático, não de query.
- Trocar por S3 é escrever `ArmazenamentoS3` e mudar uma linha no
  composition root — o domínio nem fica sabendo.

**Contra**

- Banco e disco podem divergir: um arquivo órfão sobrevive se o processo morrer
  entre gravar a imagem e persistir o cadastro.
- Com disco local, a API não escala horizontalmente (lacuna L4).
- Em container, exige volume — sem ele, as imagens somem no deploy.

**Mitigação:** a ordem das operações protege o caso que mais dói. Na troca de
foto, a nova é gravada e persistida **antes** de a antiga ser apagada; na
remoção, o arquivo só é apagado depois que o registro sai do banco. O pior caso
é lixo em disco, nunca um cadastro apontando para imagem inexistente — e há
teste de unidade para as duas ordens.
