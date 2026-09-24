"""O adaptador Motor contra um MongoDB de verdade.

Vale principalmente pelo pipeline de agregação: um fake pode aceitar um
pipeline que o Mongo real recusaria.
"""

import pytest

from app.domain.entities.avaliacao import Avaliacao, EstatisticasDeAvaliacao
from app.infrastructure.repositories.avaliacao_mongo import AvaliacaoRepositorioMongo

pytestmark = pytest.mark.db


def _avaliacao(nota: int, palestrante_id: int = 1) -> Avaliacao:
    return Avaliacao(
        palestrante_id=palestrante_id,
        autor="Grace Hopper",
        nota=nota,
        comentario="Ótima palestra",
        tags=["didática"],
    )


async def test_criar_e_listar(colecao_mongo):
    repo = AvaliacaoRepositorioMongo(colecao_mongo)

    criada = await repo.criar(_avaliacao(5))

    assert criada.id
    assert criada.criado_em is not None
    assert criada.tags == ["didática"]

    listadas = await repo.listar_por_palestrante(1)
    assert [a.id for a in listadas] == [criada.id]


async def test_listagem_e_por_palestrante_e_mais_recente_primeiro(colecao_mongo):
    repo = AvaliacaoRepositorioMongo(colecao_mongo)
    primeira = await repo.criar(_avaliacao(4))
    segunda = await repo.criar(_avaliacao(2))
    await repo.criar(_avaliacao(5, palestrante_id=2))

    listadas = await repo.listar_por_palestrante(1)

    assert [a.id for a in listadas] == [segunda.id, primeira.id]


async def test_agregacao_conta_por_nota(colecao_mongo):
    repo = AvaliacaoRepositorioMongo(colecao_mongo)
    for nota in (5, 5, 3):
        await repo.criar(_avaliacao(nota))
    await repo.criar(_avaliacao(1, palestrante_id=2))

    contagem = await repo.contar_por_nota(1)

    assert contagem == {5: 2, 3: 1}
    stats = EstatisticasDeAvaliacao.de_contagem(1, contagem)
    assert stats.total == 3
    assert stats.media == 4.33


async def test_agregacao_sem_documentos(colecao_mongo):
    assert await AvaliacaoRepositorioMongo(colecao_mongo).contar_por_nota(99) == {}
