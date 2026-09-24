# 01 — Visão da arquitetura (Fase Preliminar + Fase A)

## Escopo

API REST para gerenciar **palestrantes** e as **avaliações** das suas palestras.
Dois tipos de dado com naturezas diferentes convivendo no mesmo fluxo de
request: o cadastro do palestrante, estruturado e com integridade obrigatória, e
as avaliações do público, flexíveis e de alto volume.

Fora do escopo: front-end, emissão de certificados, venda de ingressos,
integração com sistemas de RH.

## Stakeholders e suas preocupações

| Stakeholder | Preocupação principal | Como a arquitetura responde |
|-------------|----------------------|------------------------------|
| Organizador do evento | Cadastrar e corrigir palestrantes rápido, sem perder dados | CRUD transacional no PostgreSQL, com migrations versionadas |
| Participante | Avaliar a palestra e ver a reputação de quem palestrou | Avaliações no MongoDB + endpoint de estatísticas agregadas |
| Pessoa desenvolvedora | Entender, alterar e testar sem medo | Clean Architecture, 120 testes, CI bloqueando regressão |
| Responsável pela operação | Subir em qualquer ambiente e saber que está saudável | Container, `/health`, configuração por variável de ambiente |

## Princípios de arquitetura

1. **O banco é escolhido pela natureza do dado**, não por preferência — ver
   [ADR-0001](adr/0001-dois-bancos-por-natureza-do-dado.md).
2. **A regra de negócio não conhece framework.** O domínio não importa FastAPI,
   SQLAlchemy nem PyJWT — ver [ADR-0002](adr/0002-clean-architecture.md).
3. **Dependência aponta para dentro.** Infraestrutura depende do domínio; o
   contrário nunca.
4. **O schema evolui de forma versionada**, jamais por `create_all` —
   ver [ADR-0004](adr/0004-migrations-alembic.md).
5. **Segredo não vive no repositório.** Configuração vem do ambiente.
6. **O que não tem teste não está pronto.** Cobertura mínima verificada no CI.

## Requisitos

### Funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | Cadastrar, listar, detalhar, editar e remover palestrantes |
| RF-02 | Anexar uma foto ao palestrante e trocá-la, removendo a anterior |
| RF-03 | Buscar palestrantes por nome ou local, com paginação |
| RF-04 | Registrar avaliação (autor, nota 1–5, comentário, tags) de um palestrante existente |
| RF-05 | Listar as avaliações de um palestrante, mais recentes primeiro |
| RF-06 | Apresentar média, total e distribuição das notas |
| RF-07 | Registrar usuário e autenticar por token |

### Não funcionais

| ID | Requisito | Verificação |
|----|-----------|-------------|
| RNF-01 | Escrita só com credencial válida; leitura pública | `tests/integration/test_auth_api.py` |
| RNF-02 | Senha nunca persistida em texto puro | `tests/unit/test_casos_de_uso_auth.py` |
| RNF-03 | Suíte de testes roda sem serviço externo | `tests/unit/`, `tests/integration/` |
| RNF-04 | Comportamento específico de cada banco é testado contra o banco real | `tests/db/` (job `integracao-bancos`) |
| RNF-05 | Cobertura de testes ≥ 95% | `pytest --cov --cov-fail-under=95` no CI |
| RNF-06 | Subir o ambiente completo em um comando | `make docker-up` |
| RNF-07 | Trocar um adaptador (ex.: disco → S3) sem tocar em regra de negócio | Portas em `app/domain/ports/` |
