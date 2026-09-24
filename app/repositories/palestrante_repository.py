from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.palestrante import Palestrante


class PalestranteRepository:
    """Acesso a dados relacional (PostgreSQL) para palestrantes."""

    def __init__(self, db: Session):
        self.db = db

    def list(
        self, q: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[Palestrante]:
        stmt = select(Palestrante).order_by(Palestrante.id)
        if q:
            # Busca por nome ou local — ILIKE no Postgres, LIKE no SQLite dos testes.
            termo = f"%{q}%"
            stmt = stmt.where(
                or_(Palestrante.nome.ilike(termo), Palestrante.local.ilike(termo))
            )
        return list(self.db.scalars(stmt.offset(skip).limit(limit)))

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
