# ADR-0005 — JWT sem estado; escrita autenticada, leitura pública

**Status:** Aceita · **Data:** 2026-09 · **Contexto TOGAF:** Fase D (Segurança)

## Contexto

A API precisava de controle de escrita: qualquer um podia criar, editar e
apagar palestrantes. A leitura, por outro lado, é o produto — o catálogo de
palestrantes e a reputação deles existem para serem vistos.

## Decisão

- **Leitura pública**, **escrita autenticada** (`POST`, `PUT`, `DELETE`).
- Login no padrão **OAuth2 password flow**, que o Swagger entende: o botão
  *Authorize* do `/docs` funciona sem configuração extra.
- Access token **JWT HS256**, com `sub` (e-mail) e `exp`, validado a cada
  request. Sem sessão no servidor.
- Senha em **bcrypt**, com custo configurável.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Sessão em banco/Redis | Permite revogação imediata, mas adiciona estado e mais uma infraestrutura |
| API key fixa | Simples demais: não identifica quem fez o quê e não expira |
| OAuth2 com provedor externo | Fora de escopo para um projeto que precisa rodar offline |
| **JWT sem estado** | **Escolhida** |

## Consequências

**A favor**

- O servidor não guarda sessão: escala horizontalmente sem estado compartilhado.
- O token expira sozinho.
- O fluxo é padrão e já integrado ao `/docs`.
- A senha nunca é persistida em texto puro, e o custo baixo nos testes mantém a
  suíte rápida sem enfraquecer a produção.

**Contra**

- **Não há revogação**: um token vazado vale até expirar (lacuna L5).
- Sem refresh token, a sessão cai de hora em hora.
- `JWT_SECRET` tem default de desenvolvimento — precisa ser trocado em produção,
  e nada no código obriga isso ainda.
- Sem rate limiting, o login está exposto a força bruta (lacuna L6).

**Mitigação parcial:** a expiração é curta e o login responde igual para e-mail
inexistente e senha errada, para não confirmar quais contas existem.
