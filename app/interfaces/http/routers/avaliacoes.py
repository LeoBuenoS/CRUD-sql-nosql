"""Endpoints de avaliações (MongoDB)."""

from fastapi import APIRouter, Depends, status

from app.application.use_cases import avaliacoes as casos
from app.domain.entities.usuario import Usuario
from app.interfaces.http import deps
from app.interfaces.http.schemas.avaliacao import (
    AvaliacaoIn,
    AvaliacaoOut,
    EstatisticasOut,
)

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


@router.post("", response_model=AvaliacaoOut, status_code=status.HTTP_201_CREATED)
async def criar(
    payload: AvaliacaoIn,
    caso: casos.CriarAvaliacao = Depends(deps.criar_avaliacao),
    _: Usuario = Depends(deps.usuario_atual),
):
    return AvaliacaoOut.de_entidade(await caso.executar(payload.para_entidade()))


@router.get("/{palestrante_id}", response_model=list[AvaliacaoOut])
async def listar(
    palestrante_id: int,
    caso: casos.ListarAvaliacoes = Depends(deps.listar_avaliacoes),
):
    return [AvaliacaoOut.de_entidade(a) for a in await caso.executar(palestrante_id)]


@router.get("/{palestrante_id}/estatisticas", response_model=EstatisticasOut)
async def estatisticas(
    palestrante_id: int,
    caso: casos.ObterEstatisticas = Depends(deps.obter_estatisticas),
):
    return EstatisticasOut.de_entidade(await caso.executar(palestrante_id))
