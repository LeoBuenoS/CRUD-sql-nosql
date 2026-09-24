.PHONY: help up down install run test lint fmt docker-up

help:
	@echo "up       - sobe PostgreSQL + MongoDB (docker compose)"
	@echo "docker-up- sobe a stack completa (API + bancos) em container"
	@echo "down     - derruba os containers"
	@echo "install  - instala dependencias de dev"
	@echo "run      - inicia a API (http://localhost:8000/docs)"
	@echo "test     - roda a suite de testes"
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

run:
	uvicorn app.main:app --reload

test:
	pytest -q

lint:
	flake8 app tests

fmt:
	black app tests
