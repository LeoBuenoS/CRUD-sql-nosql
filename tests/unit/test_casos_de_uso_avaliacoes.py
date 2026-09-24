from datetime import date, time

import pytest

from app.application.use_cases import avaliacoes as casos
from app.domain.entities.avaliacao import Avaliacao
from app.domain.entities.palestrante import Palestrante
from app.domain.errors import RecursoNaoEncontrado

from tests.unit.fakes import AvaliacaoRepositorioFake, PalestranteRepositorioFake

pytestmark = pytest.mark.asyncio

PALESTRANTE = Palestrante(
    nome="Ada Lovelace",
    qualificacao="Matemática",
    experiencia=10,
    data_palestra=date(2025, 9, 1),
    hora_palestra=time(14, 30),
    local="Auditório 1",
)


@pytest.fixture
def palestrantes():
    return PalestranteRepositorioFake([PALESTRANTE])


@pytest.fixture
def avaliacoes():
    return AvaliacaoRepositorioFake()


def _avaliacao(nota: int = 5, palestrante_id: int = 1) -> Avaliacao:
    return Avaliacao(palestrante_id=palestrante_id, autor="Grace", nota=nota)


async def test_criar_avaliacao(palestrantes, avaliacoes):
    criada = await casos.CriarAvaliacao(palestrantes, avaliacoes).executar(_avaliacao())

    assert criada.id is not None
    assert criada.criado_em is not None
    assert avaliacoes.itens == [criada]


async def test_criar_para_palestrante_inexistente(palestrantes, avaliacoes):
    # A consistência entre os dois bancos é responsabilidade do caso de uso.
    with pytest.raises(RecursoNaoEncontrado):
        await casos.CriarAvaliacao(palestrantes, avaliacoes).executar(
            _avaliacao(palestrante_id=999)
        )

    assert avaliacoes.itens == []


async def test_listar_so_traz_as_do_palestrante(palestrantes, avaliacoes):
    palestrantes.criar(PALESTRANTE)  # id 2
    criar = casos.CriarAvaliacao(palestrantes, avaliacoes)
    await criar.executar(_avaliacao(nota=4))
    await criar.executar(_avaliacao(nota=2))
    await criar.executar(_avaliacao(nota=5, palestrante_id=2))

    encontradas = await casos.ListarAvaliacoes(avaliacoes).executar(1)

    assert {a.nota for a in encontradas} == {4, 2}


async def test_estatisticas_agregam_as_notas(palestrantes, avaliacoes):
    criar = casos.CriarAvaliacao(palestrantes, avaliacoes)
    for nota in (5, 4, 3):
        await criar.executar(_avaliacao(nota=nota))

    stats = await casos.ObterEstatisticas(palestrantes, avaliacoes).executar(1)

    assert stats.total == 3
    assert stats.media == 4.0
    assert stats.distribuicao == {1: 0, 2: 0, 3: 1, 4: 1, 5: 1}


async def test_estatisticas_de_palestrante_inexistente(palestrantes, avaliacoes):
    with pytest.raises(RecursoNaoEncontrado):
        await casos.ObterEstatisticas(palestrantes, avaliacoes).executar(999)
