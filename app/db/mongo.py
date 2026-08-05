from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client = AsyncIOMotorClient(settings.mongo_uri)
mongo_db = client[settings.mongo_db]


def get_avaliacoes_collection():
    """Coleção NoSQL: avaliações das palestras (documento flexível)."""
    return mongo_db["avaliacoes"]
