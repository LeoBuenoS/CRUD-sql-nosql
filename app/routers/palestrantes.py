from datetime import date, time

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.deps import usuario_atual
from app.db.postgres import get_db
from app.models.palestrante import Palestrante
from app.models.usuario import Usuario
from app.repositories.palestrante_repository import PalestranteRepository
from app.schemas.palestrante import PalestranteOut
from app.services.upload import delete_upload, save_upload

router = APIRouter(prefix="/palestrantes", tags=["palestrantes"])


def _serialize(request: Request, p: Palestrante) -> PalestranteOut:
    """Monta a saída incluindo a URL pública da imagem."""
    foto_url = (
        f"{str(request.base_url).rstrip('/')}/static/uploads/{p.foto}"
        if p.foto
        else None
    )
    return PalestranteOut(
        id=p.id,
        nome=p.nome,
        qualificacao=p.qualificacao,
        experiencia=p.experiencia,
        data_palestra=p.data_palestra,
        hora_palestra=p.hora_palestra,
        local=p.local,
        foto=p.foto,
        foto_url=foto_url,
    )


@router.get("", response_model=list[PalestranteOut])
def listar(
    request: Request,
    q: str | None = Query(None, description="Busca por nome ou local"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    palestrantes = PalestranteRepository(db).list(q=q, skip=skip, limit=limit)
    return [_serialize(request, p) for p in palestrantes]


@router.get("/{palestrante_id}", response_model=PalestranteOut)
def detalhar(palestrante_id: int, request: Request, db: Session = Depends(get_db)):
    p = PalestranteRepository(db).get(palestrante_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Palestrante não encontrado")
    return _serialize(request, p)


# multipart/form-data: campos via Form(...) + arquivo via UploadFile.
# É o equivalente ao [HttpPost] Create do .NET, que recebia a ViewModel + IFormFile.
@router.post("", response_model=PalestranteOut, status_code=status.HTTP_201_CREATED)
def criar(
    request: Request,
    nome: str = Form(...),
    qualificacao: str = Form(...),
    experiencia: int = Form(..., ge=0),
    data_palestra: date = Form(...),
    hora_palestra: time = Form(...),
    local: str = Form(...),
    foto: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_atual),
):
    try:
        nome_arquivo = save_upload(foto) if foto else None
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

    p = PalestranteRepository(db).create(
        {
            "nome": nome,
            "qualificacao": qualificacao,
            "experiencia": experiencia,
            "data_palestra": data_palestra,
            "hora_palestra": hora_palestra,
            "local": local,
            "foto": nome_arquivo,
        }
    )
    return _serialize(request, p)


@router.put("/{palestrante_id}", response_model=PalestranteOut)
def editar(
    palestrante_id: int,
    request: Request,
    nome: str = Form(...),
    qualificacao: str = Form(...),
    experiencia: int = Form(..., ge=0),
    data_palestra: date = Form(...),
    hora_palestra: time = Form(...),
    local: str = Form(...),
    foto: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_atual),
):
    repo = PalestranteRepository(db)
    p = repo.get(palestrante_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Palestrante não encontrado")

    dados = {
        "nome": nome,
        "qualificacao": qualificacao,
        "experiencia": experiencia,
        "data_palestra": data_palestra,
        "hora_palestra": hora_palestra,
        "local": local,
    }

    # Se veio foto nova: salva a nova e apaga a antiga (como no Edit do .NET).
    if foto:
        try:
            dados["foto"] = save_upload(foto)
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
        delete_upload(p.foto)

    return _serialize(request, repo.update(p, dados))


@router.delete("/{palestrante_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    palestrante_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_atual),
):
    repo = PalestranteRepository(db)
    p = repo.get(palestrante_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Palestrante não encontrado")
    foto = p.foto
    repo.delete(p)
    delete_upload(foto)  # remove o arquivo de imagem junto
