from datetime import datetime, timezone

from app.db import mongo


class AvaliacaoRepository:
    """Acesso a dados NoSQL (MongoDB) para avaliações de palestras."""

    def __init__(self):
        self.collection = mongo.get_avaliacoes_collection()

    async def list_by_palestrante(self, palestrante_id: int) -> list[dict]:
        docs = [
            self._serialize(d)
            async for d in self.collection.find({"palestrante_id": palestrante_id})
        ]
        docs.sort(key=lambda d: d["criado_em"], reverse=True)
        return docs

    async def create(self, data: dict) -> dict:
        data["criado_em"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(doc)

    @staticmethod
    def _serialize(doc: dict) -> dict:
        doc["id"] = str(doc.pop("_id"))
        return doc
