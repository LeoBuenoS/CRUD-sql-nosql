import io
from datetime import date, time

import pytest

from app.application.use_cases import palestrantes as casos
from app.domain.entities.palestrante import Palestrante
from app.domain.errors import DadosInvalidos, RecursoNaoEncontrado
from app.domain.ports.servicos import ArquivoBinario

from tests.unit.fakes import ArmazenamentoFake, PalestranteRepositorioFake


def _palestrante(nome: str = "Ada Lovelace", local: str = "Auditório 1") -> Palestrante:
    return Palestrante(
        nome=nome,
        qualificacao="Matemática",
        experiencia=10,
        data_palestra=date(2025, 9, 1),
        hora_palestra=time(14, 30),
        local=local,
    )


def _foto(nome: str = "retrato.png") -> ArquivoBinario:
    return ArquivoBinario(nome_original=nome, conteudo=io.BytesIO(b"binario"))


@pytest.fixture
def repo():
    return PalestranteRepositorioFake()


@pytest.fixture
def storage():
    return ArmazenamentoFake()


def test_criar_sem_foto(repo, storage):
    criado = casos.CriarPalestrante(repo, storage).executar(_palestrante())

    assert criado.id == 1
    assert criado.foto is None
    assert storage.salvos == {}


def test_criar_com_foto_guarda_o_arquivo(repo, storage):
    criado = casos.CriarPalestrante(repo, storage).executar(_palestrante(), _foto())

    assert criado.foto in storage.salvos


def test_criar_com_extensao_invalida_nao_persiste(repo, storage):
    with pytest.raises(DadosInvalidos):
        casos.CriarPalestrante(repo, storage).executar(
            _palestrante(), _foto("virus.txt")
        )

    assert repo.itens == {}


def test_obter_inexistente(repo):
    with pytest.raises(RecursoNaoEncontrado):
        casos.ObterPalestrante(repo).executar(999)


def test_listar_filtra_e_pagina(repo, storage):
    criar = casos.CriarPalestrante(repo, storage)
    criar.executar(_palestrante("Ada Lovelace"))
    criar.executar(_palestrante("Grace Hopper"))
    criar.executar(_palestrante("Alan Turing", local="Sala Grace"))

    listar = casos.ListarPalestrantes(repo)
    assert len(listar.executar()) == 3
    # A busca cobre nome E local.
    assert {p.nome for p in listar.executar(busca="grace")} == {
        "Grace Hopper",
        "Alan Turing",
    }
    assert [p.nome for p in listar.executar(pular=1, limite=1)] == ["Grace Hopper"]


def test_editar_sem_foto_preserva_a_imagem_atual(repo, storage):
    criado = casos.CriarPalestrante(repo, storage).executar(_palestrante(), _foto())

    editado = casos.EditarPalestrante(repo, storage).executar(
        criado.id, _palestrante(nome="Ada L.")
    )

    assert editado.nome == "Ada L."
    assert editado.foto == criado.foto
    assert storage.removidos == []


def test_editar_com_foto_nova_apaga_a_antiga(repo, storage):
    criado = casos.CriarPalestrante(repo, storage).executar(_palestrante(), _foto())

    editado = casos.EditarPalestrante(repo, storage).executar(
        criado.id, _palestrante(), _foto("nova.png")
    )

    assert editado.foto != criado.foto
    assert storage.removidos == [criado.foto]


def test_editar_inexistente(repo, storage):
    with pytest.raises(RecursoNaoEncontrado):
        casos.EditarPalestrante(repo, storage).executar(999, _palestrante())


def test_remover_apaga_a_imagem_junto(repo, storage):
    criado = casos.CriarPalestrante(repo, storage).executar(_palestrante(), _foto())

    casos.RemoverPalestrante(repo, storage).executar(criado.id)

    assert repo.itens == {}
    assert storage.removidos == [criado.foto]


def test_remover_inexistente(repo, storage):
    with pytest.raises(RecursoNaoEncontrado):
        casos.RemoverPalestrante(repo, storage).executar(999)
