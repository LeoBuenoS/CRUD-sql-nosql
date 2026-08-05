from datetime import datetime

from pydantic import BaseModel, Field


class AvaliacaoCreate(BaseModel):
    palestrante_id: int
    autor: str = Field(min_length=1, max_length=120)
    nota: int = Field(ge=1, le=5)
    comentario: str | None = None
    tags: list[str] = Field(default_factory=list)


class AvaliacaoOut(AvaliacaoCreate):
    id: str
    criado_em: datetime
