from datetime import datetime, timedelta, timezone

import jwt

from app.infrastructure.config import settings

ALGORITMO = "HS256"


class EmissorDeTokenJWT:
    """Adaptador da porta EmissorDeToken: JWT HS256 com `sub` e `exp`."""

    def emitir(self, sujeito: str) -> str:
        expira_em = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expire_minutes
        )
        return jwt.encode(
            {"sub": sujeito, "exp": expira_em},
            settings.jwt_secret,
            algorithm=ALGORITMO,
        )

    def ler(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITMO])
        except jwt.PyJWTError:
            return None
        return payload.get("sub")
