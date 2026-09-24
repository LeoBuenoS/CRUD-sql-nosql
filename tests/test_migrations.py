"""As migrations são a fonte da verdade do schema — estes testes garantem que
ela não fique para trás dos models.

Rodam em SQLite (arquivo temporário), então não exigem PostgreSQL no CI.
"""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.db.postgres import Base


def _config(tmp_path) -> tuple[Config, str]:
    url = f"sqlite:///{tmp_path / 'migrations.db'}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    return config, url


def test_upgrade_cria_o_schema(tmp_path):
    config, url = _config(tmp_path)
    command.upgrade(config, "head")

    inspetor = inspect(create_engine(url))
    assert "palestrantes" in inspetor.get_table_names()
    indices = {i["name"] for i in inspetor.get_indexes("palestrantes")}
    assert "ix_palestrantes_nome" in indices


def test_schema_migrado_bate_com_os_models(tmp_path):
    config, url = _config(tmp_path)
    command.upgrade(config, "head")

    # Nenhuma diferença pendente = não falta migration para os models atuais.
    with create_engine(url).connect() as conexao:
        contexto = MigrationContext.configure(conexao)
        assert compare_metadata(contexto, Base.metadata) == []


def test_downgrade_desfaz_tudo(tmp_path):
    config, url = _config(tmp_path)
    command.upgrade(config, "head")
    command.downgrade(config, "base")

    assert "palestrantes" not in inspect(create_engine(url)).get_table_names()
