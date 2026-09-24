from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class PalestranteBase(BaseModel):
    """Campos de negócio — equivale à PalestranteViewModel (sem o IFormFile)."""

    nome: str = Field(min_length=1, max_length=200)
    qualificacao: str = Field(min_length=1, max_length=200)
    experiencia: int = Field(ge=0)
    data_palestra: date
    hora_palestra: time
    local: str = Field(min_length=1, max_length=200)


class PalestranteOut(PalestranteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    foto: str | None = None  # nome do arquivo salvo
    foto_url: str | None = None  # URL pública para exibir a imagem
