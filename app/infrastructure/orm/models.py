"""Modelos do SQLAlchemy — detalhe de persistência, não entidades de negócio.

A conversão ORM ↔ entidade acontece nos repositórios
(app/infrastructure/repositories/), para que o domínio não conheça SQLAlchemy.
"""

from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.postgres import Base


class PalestranteORM(Base):
    __tablename__ = "palestrantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), index=True)
    qualificacao: Mapped[str] = mapped_column(String(200))
    experiencia: Mapped[int] = mapped_column(Integer)
    data_palestra: Mapped[date] = mapped_column(Date)
    hora_palestra: Mapped[time] = mapped_column(Time)
    local: Mapped[str] = mapped_column(String(200))
    # Guarda o NOME do arquivo; o binário fica no armazenamento.
    foto: Mapped[str | None] = mapped_column(String(255), nullable=True)


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
