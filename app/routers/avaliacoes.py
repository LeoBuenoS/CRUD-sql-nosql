from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.mongo import get_avaliacoes_collection
from app.db.postgres import get_db
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.palestrante_repository import PalestranteRepository
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoOut, AvaliacaoStats

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


def _repo(collection=Depends(get_avaliacoes_collection)) -> AvaliacaoRepository:
    return AvaliacaoRepository(collection)


def _exige_palestrante(palestrante_id: int, db: Session) -> None:
    if not PalestranteRepository(db).get(palestrante_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Palestrante não encontrado")


@router.post("", response_model=AvaliacaoOut, status_code=status.HTTP_201_CREATED)
async def criar(
    payload: AvaliacaoCreate,
    db: Session = Depends(get_db),
    repo: AvaliacaoRepository = Depends(_repo),
):
    # O palestrante vive no Postgres; a avaliação, no Mongo.
    # A consistência entre os dois bancos é garantida aqui, no request.
    _exige_palestrante(payload.palestrante_id, db)
    return await repo.create(payload.model_dump())


@router.get("/{palestrante_id}", response_model=list[AvaliacaoOut])
async def listar(palestrante_id: int, repo: AvaliacaoRepository = Depends(_repo)):
    return await repo.list_by_palestrante(palestrante_id)


@router.get("/{palestrante_id}/estatisticas", response_model=AvaliacaoStats)
async def estatisticas(
    palestrante_id: int,
    db: Session = Depends(get_db),
    repo: AvaliacaoRepository = Depends(_repo),
):
    _exige_palestrante(palestrante_id, db)
    return await repo.stats_by_palestrante(palestrante_id)
