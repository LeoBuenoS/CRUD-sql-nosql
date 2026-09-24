from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.avaliacao import Avaliacao, EstatisticasDeAvaliacao


class AvaliacaoIn(BaseModel):
    palestrante_id: int
    autor: str = Field(min_length=1, max_length=120)
    nota: int = Field(ge=1, le=5)
    comentario: str | None = None
    tags: list[str] = Field(default_factory=list)

    def para_entidade(self) -> Avaliacao:
        return Avaliacao(**self.model_dump())


class AvaliacaoOut(BaseModel):
    id: str
    palestrante_id: int
    autor: str
    nota: int
    comentario: str | None = None
    tags: list[str] = Field(default_factory=list)
    criado_em: datetime

    @classmethod
    def de_entidade(cls, avaliacao: Avaliacao) -> "AvaliacaoOut":
        return cls(
            id=avaliacao.id,
            palestrante_id=avaliacao.palestrante_id,
            autor=avaliacao.autor,
            nota=avaliacao.nota,
            comentario=avaliacao.comentario,
            tags=avaliacao.tags,
            criado_em=avaliacao.criado_em,
        )


class EstatisticasOut(BaseModel):
    """Resumo das avaliações de um palestrante (agregação no MongoDB)."""

    palestrante_id: int
    total: int
    media: float | None = None
    distribuicao: dict[str, int]  # nota ("1".."5") -> quantidade

    @classmethod
    def de_entidade(cls, stats: EstatisticasDeAvaliacao) -> "EstatisticasOut":
        return cls(
            palestrante_id=stats.palestrante_id,
            total=stats.total,
            media=stats.media,
            distribuicao={str(nota): qtd for nota, qtd in stats.distribuicao.items()},
        )
