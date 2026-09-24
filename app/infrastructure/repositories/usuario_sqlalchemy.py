from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.usuario import Usuario
from app.infrastructure.orm.models import UsuarioORM


class UsuarioRepositorioSQLAlchemy:
    """Adaptador PostgreSQL da porta UsuarioRepositorio."""

    def __init__(self, db: Session):
        self.db = db

    def obter_por_email(self, email: str) -> Usuario | None:
        registro = self.db.scalar(select(UsuarioORM).where(UsuarioORM.email == email))
        return self._para_entidade(registro) if registro else None

    def criar(self, usuario: Usuario) -> Usuario:
        registro = UsuarioORM(email=usuario.email, senha_hash=usuario.senha_hash)
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return self._para_entidade(registro)

    @staticmethod
    def _para_entidade(registro: UsuarioORM) -> Usuario:
        return Usuario(
            id=registro.id,
            email=registro.email,
            senha_hash=registro.senha_hash,
            criado_em=registro.criado_em,
        )
