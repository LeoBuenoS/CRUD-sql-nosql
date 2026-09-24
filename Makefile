.PHONY: help up down install run test lint fmt docker-up migrate migration downgrade

help:
	@echo "up       - sobe PostgreSQL + MongoDB (docker compose)"
	@echo "docker-up- sobe a stack completa (API + bancos) em container"
	@echo "down     - derruba os containers"
	@echo "install  - instala dependencias de dev"
	@echo "migrate  - aplica as migrations (alembic upgrade head)"
	@echo "migration- cria uma migration a partir dos models (m='mensagem')"
	@echo "downgrade- desfaz a ultima migration"
	@echo "run      - inicia a API (http://localhost:8000/docs)"
	@echo "test     - roda a suite (unit + integracao, sem banco externo)"
	@echo "cov      - roda a suite com relatorio de cobertura"
	@echo "test-db  - roda os testes contra PostgreSQL e MongoDB de verdade"
	@echo "lint     - flake8"
	@echo "fmt      - black"

up:
	docker compose up -d

docker-up:
	docker compose up -d --build

down:
	docker compose down

install:
	pip install -r requirements-dev.txt

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

downgrade:
	alembic downgrade -1

run:
	uvicorn app.main:app --reload

test:
	pytest -q

cov:
	pytest -q --cov --cov-fail-under=95

test-db:
	TEST_POSTGRES_URL=postgresql+psycopg://app:change-me@localhost:5432/catalog \
	TEST_MONGO_URI=mongodb://localhost:27017 pytest -q -m db

lint:
	flake8 app tests migrations

fmt:
	black app tests migrations
