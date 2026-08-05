from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.palestrante_repository import PalestranteRepository
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoOut

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


@router.post("", response_model=AvaliacaoOut, status_code=status.HTTP_201_CREATED)
async def criar(payload: AvaliacaoCreate, db: Session = Depends(get_db)):
    if not PalestranteRepository(db).get(payload.palestrante_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Palestrante não encontrado")
    return await AvaliacaoRepository().create(payload.model_dump())


@router.get("/{palestrante_id}", response_model=list[AvaliacaoOut])
async def listar(palestrante_id: int):
    return await AvaliacaoRepository().list_by_palestrante(palestrante_id)
