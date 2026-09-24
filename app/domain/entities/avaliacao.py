from dataclasses import dataclass, field
from datetime import datetime

from app.domain.errors import DadosInvalidos

NOTA_MINIMA = 1
NOTA_MAXIMA = 5


@dataclass(frozen=True)
class Avaliacao:
    """Avaliação de uma palestra — documento flexível, guardado no MongoDB."""

    palestrante_id: int
    autor: str
    nota: int
    comentario: str | None = None
    tags: list[str] = field(default_factory=list)
    criado_em: datetime | None = None
    id: str | None = None

    def __post_init__(self) -> None:
        if not self.autor or not self.autor.strip():
            raise DadosInvalidos("autor é obrigatório")
        if not NOTA_MINIMA <= self.nota <= NOTA_MAXIMA:
            raise DadosInvalidos(f"nota deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}")


@dataclass(frozen=True)
class EstatisticasDeAvaliacao:
    """Resumo das notas de um palestrante.

    A contagem por nota vem do banco (agregação no Mongo); a média e o total
    são derivados aqui, onde a regra é testável sem infraestrutura.
    """

    palestrante_id: int
    total: int
    media: float | None
    distribuicao: dict[int, int]

    @classmethod
    def de_contagem(
        cls, palestrante_id: int, contagem_por_nota: dict[int, int]
    ) -> "EstatisticasDeAvaliacao":
        distribuicao = {
            nota: contagem_por_nota.get(nota, 0)
            for nota in range(NOTA_MINIMA, NOTA_MAXIMA + 1)
        }
        total = sum(distribuicao.values())
        soma = sum(nota * quantidade for nota, quantidade in distribuicao.items())
        return cls(
            palestrante_id=palestrante_id,
            total=total,
            media=round(soma / total, 2) if total else None,
            distribuicao=distribuicao,
        )
