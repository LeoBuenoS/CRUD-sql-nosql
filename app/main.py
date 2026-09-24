"""Ponto de entrada: monta a aplicação a partir das camadas.

Dependência aponta só para dentro:
    interfaces → application → domain
    infrastructure → domain   (implementa as portas)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.infrastructure.config import settings
from app.interfaces.http.errors import registrar_tratadores
from app.interfaces.http.routers import auth, avaliacoes, palestrantes

STATIC_DIR = Path("static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # O schema do Postgres é criado pelas migrations (`make migrate`),
    # não pelo create_all: o banco evolui de forma versionada.
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Palestrantes API — CRUD SQL (PostgreSQL) + NoSQL (MongoDB)",
        version="2.0.0",
        lifespan=lifespan,
    )

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    registrar_tratadores(app)
    app.include_router(auth.router)
    app.include_router(palestrantes.router)
    app.include_router(avaliacoes.router)

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = criar_app()
