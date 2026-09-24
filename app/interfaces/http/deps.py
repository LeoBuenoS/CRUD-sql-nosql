"""Composition root do HTTP: monta os casos de uso com os adaptadores reais.

É o único lugar onde interface e infraestrutura se encontram. Trocar o Mongo
por outro banco, ou o disco por S3, se resolve aqui — nem o domínio nem os
routers mudam.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.use_cases import auth as casos_auth
from app.application.use_cases import avaliacoes as casos_avaliacoes
from app.application.use_cases import palestrantes as casos_palestrantes
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.mongo import get_avaliacoes_collection
from app.infrastructure.db.postgres import get_db
from app.infrastructure.repositories.avaliacao_mongo import AvaliacaoRepositorioMongo
from app.infrastructure.repositories.palestrante_sqlalchemy import (
    PalestranteRepositorioSQLAlchemy,
)
from app.infrastructure.repositories.usuario_sqlalchemy import (
    UsuarioRepositorioSQLAlchemy,
)
from app.infrastructure.security.bcrypt_hasher import HashDeSenhaBcrypt
from app.infrastructure.security.jwt_emissor import EmissorDeTokenJWT
from app.infrastructure.storage.local import ArmazenamentoLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# --- adaptadores ------------------------------------------------------------


def repositorio_palestrantes(
    db: Session = Depends(get_db),
) -> PalestranteRepositorioSQLAlchemy:
    return PalestranteRepositorioSQLAlchemy(db)


def repositorio_usuarios(db: Session = Depends(get_db)) -> UsuarioRepositorioSQLAlchemy:
    return UsuarioRepositorioSQLAlchemy(db)


def repositorio_avaliacoes(
    collection=Depends(get_avaliacoes_collection),
) -> AvaliacaoRepositorioMongo:
    return AvaliacaoRepositorioMongo(collection)


def armazenamento() -> ArmazenamentoLocal:
    return ArmazenamentoLocal()


def hash_de_senha() -> HashDeSenhaBcrypt:
    return HashDeSenhaBcrypt()


def emissor_de_token() -> EmissorDeTokenJWT:
    return EmissorDeTokenJWT()


# --- casos de uso: palestrantes ---------------------------------------------


def listar_palestrantes(
    repo=Depends(repositorio_palestrantes),
) -> casos_palestrantes.ListarPalestrantes:
    return casos_palestrantes.ListarPalestrantes(repo)


def obter_palestrante(
    repo=Depends(repositorio_palestrantes),
) -> casos_palestrantes.ObterPalestrante:
    return casos_palestrantes.ObterPalestrante(repo)


def criar_palestrante(
    repo=Depends(repositorio_palestrantes), storage=Depends(armazenamento)
) -> casos_palestrantes.CriarPalestrante:
    return casos_palestrantes.CriarPalestrante(repo, storage)


def editar_palestrante(
    repo=Depends(repositorio_palestrantes), storage=Depends(armazenamento)
) -> casos_palestrantes.EditarPalestrante:
    return casos_palestrantes.EditarPalestrante(repo, storage)


def remover_palestrante(
    repo=Depends(repositorio_palestrantes), storage=Depends(armazenamento)
) -> casos_palestrantes.RemoverPalestrante:
    return casos_palestrantes.RemoverPalestrante(repo, storage)


# --- casos de uso: avaliações -----------------------------------------------


def criar_avaliacao(
    palestrantes=Depends(repositorio_palestrantes),
    avaliacoes=Depends(repositorio_avaliacoes),
) -> casos_avaliacoes.CriarAvaliacao:
    return casos_avaliacoes.CriarAvaliacao(palestrantes, avaliacoes)


def listar_avaliacoes(
    avaliacoes=Depends(repositorio_avaliacoes),
) -> casos_avaliacoes.ListarAvaliacoes:
    return casos_avaliacoes.ListarAvaliacoes(avaliacoes)


def obter_estatisticas(
    palestrantes=Depends(repositorio_palestrantes),
    avaliacoes=Depends(repositorio_avaliacoes),
) -> casos_avaliacoes.ObterEstatisticas:
    return casos_avaliacoes.ObterEstatisticas(palestrantes, avaliacoes)


# --- casos de uso: autenticação ---------------------------------------------


def registrar_usuario(
    repo=Depends(repositorio_usuarios), hasher=Depends(hash_de_senha)
) -> casos_auth.RegistrarUsuario:
    return casos_auth.RegistrarUsuario(repo, hasher)


def autenticar_usuario(
    repo=Depends(repositorio_usuarios),
    hasher=Depends(hash_de_senha),
    emissor=Depends(emissor_de_token),
) -> casos_auth.AutenticarUsuario:
    return casos_auth.AutenticarUsuario(repo, hasher, emissor)


def usuario_atual(
    token: str = Depends(oauth2_scheme),
    repo=Depends(repositorio_usuarios),
    emissor=Depends(emissor_de_token),
) -> Usuario:
    """Exigida nos endpoints de escrita; a leitura da API é pública."""
    return casos_auth.ObterUsuarioDoToken(repo, emissor).executar(token)
