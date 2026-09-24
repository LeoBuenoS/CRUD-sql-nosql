"""Dependências de autenticação."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import ler_access_token
from app.db.postgres import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

CREDENCIAIS_INVALIDAS = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Credenciais inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)


def usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Exigida nos endpoints de escrita; a leitura da API é pública."""
    email = ler_access_token(token)
    if not email:
        raise CREDENCIAIS_INVALIDAS

    usuario = UsuarioRepository(db).get_by_email(email)
    if not usuario:
        raise CREDENCIAIS_INVALIDAS
    return usuario
