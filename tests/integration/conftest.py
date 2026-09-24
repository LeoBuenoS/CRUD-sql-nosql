"""Fixtures dos testes de integração da API.

Exercitam o stack HTTP inteiro (router → caso de uso → repositório), mas com
adaptadores locais: SQLite em memória no lugar do PostgreSQL e um Mongo falso
no lugar do MongoDB. Nenhum serviço externo é necessário.
"""

import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.config import settings
from app.infrastructure.db.mongo import get_avaliacoes_collection
from app.infrastructure.db.postgres import Base, get_db
from app.infrastructure.orm import models  # noqa: F401  (registra as tabelas)
from app.interfaces.http import deps
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

CREDENCIAIS = {"email": "dev@exemplo.com", "senha": "senha-super-secreta"}

# O custo real do bcrypt deixaria a suíte lenta sem ganho de cobertura.
settings.bcrypt_rounds = 4


@pytest.fixture
def anon_client(tmp_path):
    from app.infrastructure.storage.local import ArmazenamentoLocal

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    colecao = AsyncMongoMockClient()["test"]["avaliacoes"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_avaliacoes_collection] = lambda: colecao
    # Uploads vão para um diretório temporário do teste.
    app.dependency_overrides[deps.armazenamento] = lambda: ArmazenamentoLocal(
        tmp_path / "uploads"
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(anon_client):
    """Cliente já autenticado — os endpoints de escrita exigem JWT."""
    anon_client.post("/auth/registrar", json=CREDENCIAIS)
    token = anon_client.post(
        "/auth/token",
        data={"username": CREDENCIAIS["email"], "password": CREDENCIAIS["senha"]},
    ).json()["access_token"]
    anon_client.headers["Authorization"] = f"Bearer {token}"
    return anon_client
