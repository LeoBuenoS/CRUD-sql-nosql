"""Hash de senha (bcrypt) e emissão/leitura de JWT.

A senha nunca é guardada em texto puro: o banco só vê o hash bcrypt.
O token carrega o e-mail do usuário no `sub` e um `exp` curto.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITMO = "HS256"


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(
        senha.encode(), bcrypt.gensalt(settings.bcrypt_rounds)
    ).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_access_token(sub: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    return jwt.encode(
        {"sub": sub, "exp": expira_em},
        settings.jwt_secret,
        algorithm=ALGORITMO,
    )


def ler_access_token(token: str) -> str | None:
    """Devolve o `sub` do token, ou None se for inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITMO])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
