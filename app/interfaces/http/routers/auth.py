"""Endpoints de autenticação (OAuth2 password flow + JWT)."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.use_cases import auth as casos
from app.domain.entities.usuario import Usuario
from app.interfaces.http import deps
from app.interfaces.http.schemas.usuario import Token, UsuarioIn, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registrar", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED
)
def registrar(
    payload: UsuarioIn,
    caso: casos.RegistrarUsuario = Depends(deps.registrar_usuario),
):
    return UsuarioOut.de_entidade(caso.executar(payload.email, payload.senha))


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    caso: casos.AutenticarUsuario = Depends(deps.autenticar_usuario),
) -> Token:
    """Login no padrão OAuth2 password flow (username = e-mail).

    É o que faz o botão "Authorize" do /docs funcionar.
    """
    return Token(access_token=caso.executar(form.username, form.password))


@router.get("/eu", response_model=UsuarioOut)
def eu(usuario: Usuario = Depends(deps.usuario_atual)):
    return UsuarioOut.de_entidade(usuario)
