"""indice de busca por nome

GET /palestrantes?q=... filtra por nome; o índice evita o seq scan
conforme a tabela cresce.

Revision ID: f9bf639a77a1
Revises: 252d325cec97
Create Date: 2026-09-24 15:24:30.723596

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9bf639a77a1"
down_revision: Union[str, Sequence[str], None] = "252d325cec97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_palestrantes_nome"), "palestrantes", ["nome"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_palestrantes_nome"), table_name="palestrantes")
