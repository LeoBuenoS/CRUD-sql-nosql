import bcrypt

from app.infrastructure.config import settings


class HashDeSenhaBcrypt:
    """Adaptador da porta HashDeSenha. A senha em texto nunca é persistida."""

    def gerar(self, senha: str) -> str:
        salt = bcrypt.gensalt(settings.bcrypt_rounds)
        return bcrypt.hashpw(senha.encode(), salt).decode()

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
