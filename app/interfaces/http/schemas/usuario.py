from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.usuario import SENHA_MINIMA, Usuario


class UsuarioIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=SENHA_MINIMA, max_length=128)


class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    criado_em: datetime

    @classmethod
    def de_entidade(cls, usuario: Usuario) -> "UsuarioOut":
        return cls(id=usuario.id, email=usuario.email, criado_em=usuario.criado_em)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
