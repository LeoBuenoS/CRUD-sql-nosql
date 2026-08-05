from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.palestrante import Palestrante


class PalestranteRepository:
    """Acesso a dados relacional (PostgreSQL) para palestrantes."""

    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Palestrante]:
        return list(self.db.scalars(select(Palestrante)))

    def get(self, palestrante_id: int) -> Palestrante | None:
        return self.db.get(Palestrante, palestrante_id)

    def create(self, data: dict) -> Palestrante:
        palestrante = Palestrante(**data)
        self.db.add(palestrante)
        self.db.commit()
        self.db.refresh(palestrante)
        return palestrante

    def update(self, palestrante: Palestrante, data: dict) -> Palestrante:
        for campo, valor in data.items():
            setattr(palestrante, campo, valor)
        self.db.commit()
        self.db.refresh(palestrante)
        return palestrante

    def delete(self, palestrante: Palestrante) -> None:
        self.db.delete(palestrante)
        self.db.commit()
