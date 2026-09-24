from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, avaliacoes, palestrantes

STATIC_DIR = Path("static")
(STATIC_DIR / "uploads").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # O schema do Postgres é criado pelas migrations (`make migrate`),
    # não pelo create_all: o banco evolui de forma versionada.
    yield


app = FastAPI(
    title="Palestrantes API — CRUD SQL (PostgreSQL) + NoSQL (MongoDB)",
    version="1.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(palestrantes.router)
app.include_router(avaliacoes.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
