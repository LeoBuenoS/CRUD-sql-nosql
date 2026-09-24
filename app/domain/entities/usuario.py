from dataclasses import dataclass
from datetime import datetime

from app.domain.errors import DadosInvalidos

SENHA_MINIMA = 8


@dataclass(frozen=True)
class Usuario:
    """Usuário que autentica na API. Só o hash da senha circula pelo domínio."""

    email: str
    senha_hash: str
    criado_em: datetime | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise DadosInvalidos("e-mail inválido")
