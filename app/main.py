from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.postgres import Base, engine
from app.routers import avaliacoes, palestrantes

STATIC_DIR = Path("static")
(STATIC_DIR / "uploads").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Palestrantes API — CRUD SQL (PostgreSQL) + NoSQL (MongoDB)",
    version="1.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(palestrantes.router)
app.include_router(avaliacoes.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
