from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.infrastructure.config import settings
from app.infrastructure.db.postgres import Base

# Importa os models ORM para que o autogenerate enxergue as tabelas.
from app.infrastructure.orm import models  # noqa: F401

config = context.config

# A URL vem da configuração da aplicação (.env), não do alembic.ini — assim o
# mesmo .env serve para a API e para as migrations. Quem chama o Alembic por
# código (os testes) pode sobrescrevê-la antes.
config.set_main_option(
    "sqlalchemy.url", config.get_main_option("sqlalchemy.url") or settings.postgres_url
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL sem conectar ao banco (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrations conectando ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
