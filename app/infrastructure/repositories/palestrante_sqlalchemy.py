from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.entities.palestrante import Palestrante
from app.infrastructure.orm.models import PalestranteORM


class PalestranteRepositorioSQLAlchemy:
    """Adaptador PostgreSQL da porta PalestranteRepositorio."""

    def __init__(self, db: Session):
        self.db = db

    def listar(
        self, busca: str | None = None, pular: int = 0, limite: int = 50
    ) -> list[Palestrante]:
        stmt = select(PalestranteORM).order_by(PalestranteORM.id)
        if busca:
            # ILIKE no Postgres; no SQLite dos testes vira LIKE case-insensitive.
            termo = f"%{busca}%"
            stmt = stmt.where(
                or_(PalestranteORM.nome.ilike(termo), PalestranteORM.local.ilike(termo))
            )
        registros = self.db.scalars(stmt.offset(pular).limit(limite))
        return [self._para_entidade(r) for r in registros]

    def obter(self, palestrante_id: int) -> Palestrante | None:
        registro = self.db.get(PalestranteORM, palestrante_id)
        return self._para_entidade(registro) if registro else None

    def criar(self, palestrante: Palestrante) -> Palestrante:
        registro = PalestranteORM(**self._campos(palestrante))
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return self._para_entidade(registro)

    def atualizar(self, palestrante: Palestrante) -> Palestrante:
        registro = self.db.get(PalestranteORM, palestrante.id)
        for campo, valor in self._campos(palestrante).items():
            setattr(registro, campo, valor)
        self.db.commit()
        self.db.refresh(registro)
        return self._para_entidade(registro)

    def remover(self, palestrante_id: int) -> None:
        registro = self.db.get(PalestranteORM, palestrante_id)
        if registro:
            self.db.delete(registro)
            self.db.commit()

    @staticmethod
    def _campos(palestrante: Palestrante) -> dict:
        return {
            "nome": palestrante.nome,
            "qualificacao": palestrante.qualificacao,
            "experiencia": palestrante.experiencia,
            "data_palestra": palestrante.data_palestra,
            "hora_palestra": palestrante.hora_palestra,
            "local": palestrante.local,
            "foto": palestrante.foto,
        }

    @staticmethod
    def _para_entidade(registro: PalestranteORM) -> Palestrante:
        return Palestrante(
            id=registro.id,
            nome=registro.nome,
            qualificacao=registro.qualificacao,
            experiencia=registro.experiencia,
            data_palestra=registro.data_palestra,
            hora_palestra=registro.hora_palestra,
            local=registro.local,
            foto=registro.foto,
        )
