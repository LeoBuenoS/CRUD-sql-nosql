import pytest

from app.application.use_cases import auth as casos
from app.domain.errors import ConflitoDeDados, CredenciaisInvalidas, DadosInvalidos

from tests.unit.fakes import (
    EmissorDeTokenFake,
    HashDeSenhaFake,
    UsuarioRepositorioFake,
)

EMAIL = "dev@exemplo.com"
SENHA = "senha-super-secreta"


@pytest.fixture
def repo():
    return UsuarioRepositorioFake()


@pytest.fixture
def hasher():
    return HashDeSenhaFake()


def test_registrar_guarda_apenas_o_hash(repo, hasher):
    usuario = casos.RegistrarUsuario(repo, hasher).executar(EMAIL, SENHA)

    assert usuario.email == EMAIL
    assert usuario.senha_hash != SENHA
    assert hasher.verificar(SENHA, usuario.senha_hash)


def test_registrar_email_duplicado(repo, hasher):
    registrar = casos.RegistrarUsuario(repo, hasher)
    registrar.executar(EMAIL, SENHA)

    with pytest.raises(ConflitoDeDados):
        registrar.executar(EMAIL, "outra-senha-longa")


def test_registrar_senha_curta(repo, hasher):
    with pytest.raises(DadosInvalidos):
        casos.RegistrarUsuario(repo, hasher).executar(EMAIL, "curta")


def test_autenticar_devolve_token(repo, hasher):
    casos.RegistrarUsuario(repo, hasher).executar(EMAIL, SENHA)

    token = casos.AutenticarUsuario(repo, hasher, EmissorDeTokenFake()).executar(
        EMAIL, SENHA
    )

    assert token == f"token::{EMAIL}"


def test_autenticar_com_senha_errada(repo, hasher):
    casos.RegistrarUsuario(repo, hasher).executar(EMAIL, SENHA)

    with pytest.raises(CredenciaisInvalidas):
        casos.AutenticarUsuario(repo, hasher, EmissorDeTokenFake()).executar(
            EMAIL, "errada"
        )


def test_autenticar_usuario_inexistente(repo, hasher):
    with pytest.raises(CredenciaisInvalidas):
        casos.AutenticarUsuario(repo, hasher, EmissorDeTokenFake()).executar(
            EMAIL, SENHA
        )


def test_usuario_do_token(repo, hasher):
    casos.RegistrarUsuario(repo, hasher).executar(EMAIL, SENHA)

    usuario = casos.ObterUsuarioDoToken(repo, EmissorDeTokenFake()).executar(
        f"token::{EMAIL}"
    )

    assert usuario.email == EMAIL


def test_token_invalido(repo):
    with pytest.raises(CredenciaisInvalidas):
        casos.ObterUsuarioDoToken(repo, EmissorDeTokenFake(valido=False)).executar("x")


def test_token_de_usuario_removido(repo):
    # Token assinado, mas o usuário não existe mais no banco.
    with pytest.raises(CredenciaisInvalidas):
        casos.ObterUsuarioDoToken(repo, EmissorDeTokenFake()).executar(
            f"token::{EMAIL}"
        )
