# Arquitetura — visão TOGAF

Esta pasta descreve o projeto com o vocabulário do **TOGAF ADM**, nas quatro
camadas clássicas (BDAT): **Negócio**, **Dados**, **Aplicação** e **Tecnologia**.

O TOGAF é um framework de arquitetura corporativa — bem maior do que uma API de
portfólio. O que se usa aqui é a **estrutura de documentação**: registrar a
visão, as camadas, as decisões e as lacunas de forma que outra pessoa entenda o
*porquê* de cada escolha, não só o *como*. Fases do ADM que dependem de contexto
organizacional (Governança, Gestão de Mudança, Contratos de Implementação) ficam
propositalmente de fora.

| Documento | Fase do ADM | Conteúdo |
|-----------|-------------|----------|
| [01-visao.md](01-visao.md) | Preliminar + A | Escopo, stakeholders, princípios, requisitos |
| [02-negocio.md](02-negocio.md) | B | Atores, capacidades e processos de negócio |
| [03-dados.md](03-dados.md) | C (Dados) | Entidades, modelo relacional e de documento, ciclo de vida |
| [04-aplicacao.md](04-aplicacao.md) | C (Aplicação) | Camadas, componentes, portas e adaptadores |
| [05-tecnologia.md](05-tecnologia.md) | D | Stack, implantação, ambientes, qualidade |
| [06-lacunas-e-roadmap.md](06-lacunas-e-roadmap.md) | E + F | Análise de lacunas e evolução planejada |
| [adr/](adr/) | Requisitos (contínuo) | Decisões arquiteturais registradas |

## Correspondência com o código

| Camada TOGAF | Onde vive |
|--------------|-----------|
| Negócio | `app/domain/entities/` — regras que existiriam mesmo sem software |
| Aplicação | `app/application/use_cases/` e `app/interfaces/http/` |
| Dados | `app/infrastructure/orm/`, `app/infrastructure/repositories/`, `migrations/` |
| Tecnologia | `Dockerfile`, `docker-compose.yml`, `.github/workflows/` |
