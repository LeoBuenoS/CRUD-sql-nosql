"""Endpoints de palestrantes — só traduzem HTTP ↔ caso de uso."""

from datetime import date, time

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status

from app.application.use_cases import palestrantes as casos
from app.domain.entities.usuario import Usuario
from app.domain.ports.servicos import ArquivoBinario
from app.interfaces.http import deps
from app.interfaces.http.schemas.palestrante import PalestranteIn, PalestranteOut

router = APIRouter(prefix="/palestrantes", tags=["palestrantes"])


def _formulario(
    nome: str = Form(...),
    qualificacao: str = Form(...),
    experiencia: int = Form(..., ge=0),
    data_palestra: date = Form(...),
    hora_palestra: time = Form(...),
    local: str = Form(...),
) -> PalestranteIn:
    """multipart/form-data: os campos vêm como Form, a imagem como UploadFile."""
    return PalestranteIn(
        nome=nome,
        qualificacao=qualificacao,
        experiencia=experiencia,
        data_palestra=data_palestra,
        hora_palestra=hora_palestra,
        local=local,
    )


def _arquivo(foto: UploadFile | None) -> ArquivoBinario | None:
    """Converte o UploadFile do FastAPI no tipo que o domínio entende."""
    if not foto:
        return None
    return ArquivoBinario(nome_original=foto.filename or "", conteudo=foto.file)


@router.get("", response_model=list[PalestranteOut])
def listar(
    request: Request,
    q: str | None = Query(None, description="Busca por nome ou local"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    caso: casos.ListarPalestrantes = Depends(deps.listar_palestrantes),
):
    encontrados = caso.executar(busca=q, pular=skip, limite=limit)
    return [PalestranteOut.de_entidade(p, str(request.base_url)) for p in encontrados]


@router.get("/{palestrante_id}", response_model=PalestranteOut)
def detalhar(
    palestrante_id: int,
    request: Request,
    caso: casos.ObterPalestrante = Depends(deps.obter_palestrante),
):
    return PalestranteOut.de_entidade(
        caso.executar(palestrante_id), str(request.base_url)
    )


@router.post("", response_model=PalestranteOut, status_code=status.HTTP_201_CREATED)
def criar(
    request: Request,
    dados: PalestranteIn = Depends(_formulario),
    foto: UploadFile | None = File(None),
    caso: casos.CriarPalestrante = Depends(deps.criar_palestrante),
    _: Usuario = Depends(deps.usuario_atual),
):
    criado = caso.executar(dados.para_entidade(), _arquivo(foto))
    return PalestranteOut.de_entidade(criado, str(request.base_url))


@router.put("/{palestrante_id}", response_model=PalestranteOut)
def editar(
    palestrante_id: int,
    request: Request,
    dados: PalestranteIn = Depends(_formulario),
    foto: UploadFile | None = File(None),
    caso: casos.EditarPalestrante = Depends(deps.editar_palestrante),
    _: Usuario = Depends(deps.usuario_atual),
):
    atualizado = caso.executar(palestrante_id, dados.para_entidade(), _arquivo(foto))
    return PalestranteOut.de_entidade(atualizado, str(request.base_url))


@router.delete("/{palestrante_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    palestrante_id: int,
    caso: casos.RemoverPalestrante = Depends(deps.remover_palestrante),
    _: Usuario = Depends(deps.usuario_atual),
):
    caso.executar(palestrante_id)
