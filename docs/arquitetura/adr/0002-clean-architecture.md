# ADR-0002 — Clean Architecture com portas e adaptadores

**Status:** Aceita · **Data:** 2026-09 · **Contexto TOGAF:** Fase C (Aplicação)

## Contexto

A primeira versão seguia o layout comum de projeto FastAPI: `routers/`,
`repositories/`, `models/`, `schemas/`. Funciona, mas embaralha as
responsabilidades:

- a regra de negócio ficava dividida entre router e repositório;
- a validação de negócio (nota 1–5, experiência não negativa) existia só no
  schema Pydantic, ou seja, só valia via HTTP;
- testar a regra exigia subir a aplicação inteira e um banco;
- trocar disco por S3 significaria mexer em endpoint.

## Decisão

Quatro camadas, com a dependência apontando sempre para dentro:

```
interfaces/http  →  application/use_cases  →  domain
infrastructure   →  domain (implementa as portas)
```

- `domain/`: entidades como dataclasses imutáveis, com as invariantes no
  `__post_init__`; erros de negócio; e as **portas** (`typing.Protocol`) que
  descrevem o que o domínio precisa do mundo externo.
- `application/`: um caso de uso por operação, dependendo só de portas.
- `infrastructure/`: adaptadores (SQLAlchemy, Motor, bcrypt, PyJWT, disco).
- `interfaces/http/`: routers finos, schemas de contrato e o **composition
  root** (`deps.py`), único ponto onde as escolhas concretas são amarradas.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Manter o layout por tipo de arquivo | Simples, mas a regra continua espalhada e presa ao framework |
| Camadas sem inversão de dependência (serviço chama repositório concreto) | Melhora a organização, mas o núcleo continua amarrado ao SQLAlchemy |
| **Clean Architecture com Protocols** | **Escolhida** |

## Consequências

**A favor**

- A regra de negócio roda em milissegundos, sem banco e sem HTTP.
- Trocar um adaptador é escrever outra classe e mudar uma linha no `deps.py`.
- Cada arquivo tem um motivo só para mudar.
- Os erros de domínio viram status HTTP num lugar único.

**Contra**

- Mais arquivos e uma indireção a mais: para uma API CRUD pequena, é
  deliberadamente mais estrutura do que o mínimo necessário.
- Conversão ORM ↔ entidade escrita à mão nos repositórios.
- Quem chega no projeto precisa entender a regra da dependência antes de mexer.

**Por que ainda assim vale:** o projeto é um portfólio, e o que ele demonstra é
justamente o critério de separação. A prova de que a escolha não ficou no papel
é que a refatoração inteira passou com os 26 testes de API existentes sem
alteração de comportamento.

## Como verificar

A regra não depende de disciplina de revisão: `tests/unit/test_arquitetura.py`
lê os imports de cada módulo e falha se alguém furar a camada.

```bash
pytest tests/unit/test_arquitetura.py
```

Ele garante três coisas: domínio e aplicação não importam framework nenhum;
nenhuma camada importa outra mais externa; e só o composition root
(`app/interfaces/http/deps.py`) conhece adaptador concreto.
