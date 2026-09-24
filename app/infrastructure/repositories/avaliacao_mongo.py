from datetime import datetime, timezone

from app.domain.entities.avaliacao import Avaliacao


class AvaliacaoRepositorioMongo:
    """Adaptador MongoDB da porta AvaliacaoRepositorio."""

    def __init__(self, collection):
        self.collection = collection

    async def listar_por_palestrante(self, palestrante_id: int) -> list[Avaliacao]:
        # A ordenação é do banco, não do Python: além de escalar com o volume,
        # o desempate por _id garante ordem estável. O Mongo guarda datetime
        # com precisão de milissegundo, então duas avaliações do mesmo
        # milissegundo empatam em `criado_em` — e o _id, monotônico, decide.
        cursor = self.collection.find({"palestrante_id": palestrante_id}).sort(
            [("criado_em", -1), ("_id", -1)]
        )
        return [self._para_entidade(documento) async for documento in cursor]

    async def criar(self, avaliacao: Avaliacao) -> Avaliacao:
        documento = {
            "palestrante_id": avaliacao.palestrante_id,
            "autor": avaliacao.autor,
            "nota": avaliacao.nota,
            "comentario": avaliacao.comentario,
            "tags": avaliacao.tags,
            "criado_em": avaliacao.criado_em or datetime.now(timezone.utc),
        }
        resultado = await self.collection.insert_one(documento)
        return self._para_entidade(
            await self.collection.find_one({"_id": resultado.inserted_id})
        )

    async def contar_por_nota(self, palestrante_id: int) -> dict[int, int]:
        """Agregação no Mongo: quantas avaliações há de cada nota.

        A média e o total saem da entidade EstatisticasDeAvaliacao — o banco
        entrega só a contagem, que é o que ele faz bem.
        """
        pipeline = [
            {"$match": {"palestrante_id": palestrante_id}},
            {"$group": {"_id": "$nota", "quantidade": {"$sum": 1}}},
        ]
        return {
            documento["_id"]: documento["quantidade"]
            async for documento in self.collection.aggregate(pipeline)
        }

    @staticmethod
    def _para_entidade(documento: dict) -> Avaliacao:
        return Avaliacao(
            id=str(documento["_id"]),
            palestrante_id=documento["palestrante_id"],
            autor=documento["autor"],
            nota=documento["nota"],
            comentario=documento.get("comentario"),
            tags=documento.get("tags", []),
            criado_em=documento["criado_em"],
        )
