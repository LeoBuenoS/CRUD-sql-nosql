from datetime import date, time

from sqlalchemy import Date, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base


class Palestrante(Base):
    """
    Entidade relacional (PostgreSQL).
    Equivale ao model 'Palestrante' do tutorial .NET (Entity Framework),
    mas aqui a foto guarda apenas o NOME do arquivo salvo em disco,
    não a imagem em si (o binário fica no volume, não no banco).
    """

    __tablename__ = "palestrantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), index=True)
    qualificacao: Mapped[str] = mapped_column(String(200))
    experiencia: Mapped[int] = mapped_column(Integer)
    data_palestra: Mapped[date] = mapped_column(Date)
    hora_palestra: Mapped[time] = mapped_column(Time)
    local: Mapped[str] = mapped_column(String(200))
    foto: Mapped[str | None] = mapped_column(String(255), nullable=True)
