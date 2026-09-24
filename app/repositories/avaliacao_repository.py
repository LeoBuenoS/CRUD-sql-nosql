from datetime import datetime, timezone


class AvaliacaoRepository:
    """Acesso a dados NoSQL (MongoDB) para avaliações de palestras."""

    def __init__(self, collection):
        self.collection = collection

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

    async def stats_by_palestrante(self, palestrante_id: int) -> dict:
        """Agregação no Mongo: média, total e distribuição das notas.

        É o tipo de consulta que o documento resolve bem sem join —
        o dado já chega denormalizado na coleção.
        """
        pipeline = [
            {"$match": {"palestrante_id": palestrante_id}},
            {
                "$group": {
                    "_id": "$nota",
                    "quantidade": {"$sum": 1},
                }
            },
        ]
        por_nota = {
            doc["_id"]: doc["quantidade"]
            async for doc in self.collection.aggregate(pipeline)
        }

        total = sum(por_nota.values())
        soma = sum(nota * qtd for nota, qtd in por_nota.items())
        return {
            "palestrante_id": palestrante_id,
            "total": total,
            "media": round(soma / total, 2) if total else None,
            "distribuicao": {str(nota): por_nota.get(nota, 0) for nota in range(1, 6)},
        }

    @staticmethod
    def _serialize(doc: dict) -> dict:
        doc["id"] = str(doc.pop("_id"))
        return doc
