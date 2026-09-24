import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.mongo import get_avaliacoes_collection
from app.db.postgres import Base, get_db
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
def anon_client(tmp_path, monkeypatch):
    # Redireciona os uploads para um diretório temporário do teste.
    import app.services.upload as upload_mod

    monkeypatch.setattr(upload_mod, "UPLOAD_DIR", tmp_path / "uploads")

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    # SQL em SQLite na memória, NoSQL em um Mongo falso — a suíte roda
    # sem depender de nenhum banco externo.
    colecao = AsyncMongoMockClient()["test"]["avaliacoes"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_avaliacoes_collection] = lambda: colecao

    with TestClient(app) as c:
        yield c

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
