"""Fixtures dos testes contra bancos de verdade.

Os testes de integração da API usam SQLite e um Mongo falso — rápidos, mas
cegos para o que é específico de cada banco (tipos do PostgreSQL, pipeline de
agregação do Mongo, as migrations aplicadas de fato). Estes aqui fecham essa
lacuna e rodam no job `integration-db` do CI, com os serviços no compose do
workflow. Sem as variáveis de ambiente, a suíte inteira é pulada.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
MONGO_URI = os.getenv("TEST_MONGO_URI")


@pytest.fixture(scope="session")
def engine_postgres():
    if not POSTGRES_URL:
        pytest.skip("TEST_POSTGRES_URL não definida")

    # O schema é criado pelas migrations — o mesmo caminho da produção.
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", POSTGRES_URL)
    command.upgrade(config, "head")

    engine = create_engine(POSTGRES_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def sessao_postgres(engine_postgres):
    Session = sessionmaker(bind=engine_postgres, autoflush=False, autocommit=False)
    with Session() as sessao:
        yield sessao
        sessao.rollback()

    with engine_postgres.begin() as conexao:
        conexao.execute(text("TRUNCATE palestrantes, usuarios RESTART IDENTITY"))


@pytest.fixture
async def colecao_mongo():
    if not MONGO_URI:
        pytest.skip("TEST_MONGO_URI não definida")

    cliente = AsyncIOMotorClient(MONGO_URI)
    colecao = cliente["catalog_test"]["avaliacoes"]
    await colecao.delete_many({})
    yield colecao
    await colecao.delete_many({})
    cliente.close()
