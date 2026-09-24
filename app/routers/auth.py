from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import CREDENCIAIS_INVALIDAS, usuario_atual
from app.core.security import criar_access_token, verificar_senha
from app.db.postgres import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registrar", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED
)
def registrar(payload: UsuarioCreate, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    if repo.get_by_email(payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")
    return repo.create(payload.email, payload.senha)


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """Login no formato OAuth2 password flow (username = e-mail).

    É o que faz o botão "Authorize" do /docs funcionar.
    """
    usuario = UsuarioRepository(db).get_by_email(form.username)
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise CREDENCIAIS_INVALIDAS
    return Token(access_token=criar_access_token(usuario.email))


@router.get("/eu", response_model=UsuarioOut)
def eu(usuario: Usuario = Depends(usuario_atual)):
    return usuario
