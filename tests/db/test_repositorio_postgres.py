"""O adaptador SQLAlchemy contra um PostgreSQL de verdade."""

from datetime import date, time

import pytest

from app.domain.entities.palestrante import Palestrante
from app.domain.entities.usuario import Usuario
from app.infrastructure.repositories.palestrante_sqlalchemy import (
    PalestranteRepositorioSQLAlchemy,
)
from app.infrastructure.repositories.usuario_sqlalchemy import (
    UsuarioRepositorioSQLAlchemy,
)

pytestmark = pytest.mark.db


def _palestrante(nome: str = "Ada Lovelace", local: str = "Auditório 1") -> Palestrante:
    return Palestrante(
        nome=nome,
        qualificacao="Matemática",
        experiencia=10,
        data_palestra=date(2025, 9, 1),
        hora_palestra=time(14, 30),
        local=local,
    )


def test_ciclo_completo(sessao_postgres):
    repo = PalestranteRepositorioSQLAlchemy(sessao_postgres)

    criado = repo.criar(_palestrante())
    assert criado.id is not None
    assert repo.obter(criado.id) == criado

    editado = repo.atualizar(criado.com_foto("retrato.png"))
    assert editado.foto == "retrato.png"

    repo.remover(criado.id)
    assert repo.obter(criado.id) is None


def test_busca_ilike_ignora_maiusculas(sessao_postgres):
    """ILIKE é do PostgreSQL — o SQLite dos outros testes não prova isso."""
    repo = PalestranteRepositorioSQLAlchemy(sessao_postgres)
    repo.criar(_palestrante("Grace Hopper"))
    repo.criar(_palestrante("Alan Turing", local="Sala GRACE"))
    repo.criar(_palestrante("Ada Lovelace"))

    encontrados = repo.listar(busca="grace")

    assert {p.nome for p in encontrados} == {"Grace Hopper", "Alan Turing"}


def test_paginacao(sessao_postgres):
    repo = PalestranteRepositorioSQLAlchemy(sessao_postgres)
    for i in range(3):
        repo.criar(_palestrante(f"Palestrante {i}"))

    assert [p.nome for p in repo.listar(pular=1, limite=1)] == ["Palestrante 1"]


def test_usuario_criado_recebe_criado_em_do_banco(sessao_postgres):
    """server_default=now() só é exercido contra o PostgreSQL."""
    repo = UsuarioRepositorioSQLAlchemy(sessao_postgres)

    usuario = repo.criar(Usuario(email="dev@exemplo.com", senha_hash="hash"))

    assert usuario.id is not None
    assert usuario.criado_em is not None
    assert repo.obter_por_email("dev@exemplo.com") == usuario


def test_email_duplicado_viola_o_indice_unico(sessao_postgres):
    from sqlalchemy.exc import IntegrityError

    repo = UsuarioRepositorioSQLAlchemy(sessao_postgres)
    repo.criar(Usuario(email="dev@exemplo.com", senha_hash="hash"))

    with pytest.raises(IntegrityError):
        repo.criar(Usuario(email="dev@exemplo.com", senha_hash="outro"))
