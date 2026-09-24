"""Contratos HTTP de palestrantes — entrada e saída da API.

São da camada de interface: descrevem o JSON, não a regra de negócio.
A validação de negócio está na entidade (app/domain/entities/palestrante.py).
"""

from datetime import date, time

from pydantic import BaseModel, Field

from app.domain.entities.palestrante import Palestrante


class PalestranteIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    qualificacao: str = Field(min_length=1, max_length=200)
    experiencia: int = Field(ge=0)
    data_palestra: date
    hora_palestra: time
    local: str = Field(min_length=1, max_length=200)

    def para_entidade(self) -> Palestrante:
        return Palestrante(**self.model_dump())


class PalestranteOut(BaseModel):
    id: int
    nome: str
    qualificacao: str
    experiencia: int
    data_palestra: date
    hora_palestra: time
    local: str
    foto: str | None = None  # nome do arquivo salvo
    foto_url: str | None = None  # URL pública para exibir a imagem

    @classmethod
    def de_entidade(
        cls, palestrante: Palestrante, base_url: str = ""
    ) -> "PalestranteOut":
        foto_url = (
            f"{base_url.rstrip('/')}/static/uploads/{palestrante.foto}"
            if palestrante.foto
            else None
        )
        return cls(
            id=palestrante.id,
            nome=palestrante.nome,
            qualificacao=palestrante.qualificacao,
            experiencia=palestrante.experiencia,
            data_palestra=palestrante.data_palestra,
            hora_palestra=palestrante.hora_palestra,
            local=palestrante.local,
            foto=palestrante.foto,
            foto_url=foto_url,
        )
