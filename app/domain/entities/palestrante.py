from dataclasses import dataclass, replace
from datetime import date, time

from app.domain.errors import DadosInvalidos

TAMANHO_MAXIMO_TEXTO = 200


@dataclass(frozen=True)
class Palestrante:
    """Entidade de negócio — sem ORM, sem Pydantic, sem framework.

    A `foto` guarda apenas o NOME do arquivo; o binário vive no
    armazenamento (porta ArmazenamentoDeArquivos), não no banco.
    """

    nome: str
    qualificacao: str
    experiencia: int
    data_palestra: date
    hora_palestra: time
    local: str
    foto: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        for campo in ("nome", "qualificacao", "local"):
            valor = getattr(self, campo)
            if not valor or not valor.strip():
                raise DadosInvalidos(f"{campo} é obrigatório")
            if len(valor) > TAMANHO_MAXIMO_TEXTO:
                raise DadosInvalidos(
                    f"{campo} excede {TAMANHO_MAXIMO_TEXTO} caracteres"
                )
        if self.experiencia < 0:
            raise DadosInvalidos("experiencia não pode ser negativa")

    def com_foto(self, foto: str | None) -> "Palestrante":
        """Devolve uma cópia apontando para outra imagem (entidade imutável)."""
        return replace(self, foto=foto)
