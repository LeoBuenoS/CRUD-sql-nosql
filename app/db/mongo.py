from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.core.config import settings

client = AsyncIOMotorClient(settings.mongo_uri)
mongo_db = client[settings.mongo_db]


def get_avaliacoes_collection() -> AsyncIOMotorCollection:
    """Coleção NoSQL: avaliações das palestras (documento flexível).

    Usada como dependência do FastAPI, o que permite trocar a coleção real
    por uma em memória nos testes (app.dependency_overrides).
    """
    return mongo_db["avaliacoes"]
