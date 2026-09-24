"""cria tabela palestrantes

Migration inicial: a tabela relacional do palestrante.
(As avaliações vivem no MongoDB e não têm schema versionado aqui.)

Revision ID: 252d325cec97
Revises:
Create Date: 2026-09-24 15:24:12.584380

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "252d325cec97"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "palestrantes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("qualificacao", sa.String(length=200), nullable=False),
        sa.Column("experiencia", sa.Integer(), nullable=False),
        sa.Column("data_palestra", sa.Date(), nullable=False),
        sa.Column("hora_palestra", sa.Time(), nullable=False),
        sa.Column("local", sa.String(length=200), nullable=False),
        sa.Column("foto", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("palestrantes")
