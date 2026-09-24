"""Regras de negócio puras — sem banco, sem HTTP, sem framework."""

from datetime import date, time

import pytest

from app.domain.entities.avaliacao import Avaliacao, EstatisticasDeAvaliacao
from app.domain.entities.palestrante import Palestrante
from app.domain.entities.usuario import Usuario
from app.domain.errors import DadosInvalidos

VALIDO = {
    "nome": "Ada Lovelace",
    "qualificacao": "Matemática",
    "experiencia": 10,
    "data_palestra": date(2025, 9, 1),
    "hora_palestra": time(14, 30),
    "local": "Auditório 1",
}


def test_palestrante_valido():
    palestrante = Palestrante(**VALIDO)
    assert palestrante.foto is None
    assert palestrante.id is None


@pytest.mark.parametrize("campo", ["nome", "qualificacao", "local"])
def test_campo_obrigatorio_em_branco(campo):
    with pytest.raises(DadosInvalidos):
        Palestrante(**{**VALIDO, campo: "   "})


def test_texto_longo_demais():
    with pytest.raises(DadosInvalidos):
        Palestrante(**{**VALIDO, "nome": "a" * 201})


def test_experiencia_negativa():
    with pytest.raises(DadosInvalidos):
        Palestrante(**{**VALIDO, "experiencia": -1})


def test_com_foto_nao_muta_o_original():
    original = Palestrante(**VALIDO)
    novo = original.com_foto("retrato.png")

    assert original.foto is None
    assert novo.foto == "retrato.png"
    assert novo.nome == original.nome


@pytest.mark.parametrize("nota", [0, 6, -1])
def test_nota_fora_da_faixa(nota):
    with pytest.raises(DadosInvalidos):
        Avaliacao(palestrante_id=1, autor="Grace", nota=nota)


def test_autor_obrigatorio():
    with pytest.raises(DadosInvalidos):
        Avaliacao(palestrante_id=1, autor=" ", nota=5)


def test_estatisticas_calculam_media_e_distribuicao():
    stats = EstatisticasDeAvaliacao.de_contagem(1, {5: 2, 3: 1})

    assert stats.total == 3
    assert stats.media == 4.33  # (5 + 5 + 3) / 3, arredondado
    assert stats.distribuicao == {1: 0, 2: 0, 3: 1, 4: 0, 5: 2}


def test_estatisticas_sem_avaliacoes():
    stats = EstatisticasDeAvaliacao.de_contagem(1, {})

    assert stats.total == 0
    assert stats.media is None
    assert set(stats.distribuicao) == {1, 2, 3, 4, 5}


def test_email_invalido():
    with pytest.raises(DadosInvalidos):
        Usuario(email="sem-arroba", senha_hash="x")
