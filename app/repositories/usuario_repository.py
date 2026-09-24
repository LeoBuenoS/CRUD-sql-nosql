from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_senha
from app.models.usuario import Usuario


class UsuarioRepository:
    """Acesso a dados relacional (PostgreSQL) para usuários."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def create(self, email: str, senha: str) -> Usuario:
        usuario = Usuario(email=email, senha_hash=hash_senha(senha))
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
