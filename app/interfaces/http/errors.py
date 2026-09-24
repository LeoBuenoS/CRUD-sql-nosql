"""Tradução de erro de domínio para HTTP.

Concentrar isso aqui mantém os routers limpos: eles chamam o caso de uso e
devolvem a resposta; quem decide que "não encontrado" é 404 é a interface.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    ConflitoDeDados,
    CredenciaisInvalidas,
    DadosInvalidos,
    ErroDeDominio,
    RecursoNaoEncontrado,
)

STATUS_POR_ERRO: dict[type[ErroDeDominio], int] = {
    RecursoNaoEncontrado: status.HTTP_404_NOT_FOUND,
    ConflitoDeDados: status.HTTP_409_CONFLICT,
    DadosInvalidos: status.HTTP_400_BAD_REQUEST,
    CredenciaisInvalidas: status.HTTP_401_UNAUTHORIZED,
}


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(ErroDeDominio)
    async def tratar_erro_de_dominio(_: Request, erro: ErroDeDominio) -> JSONResponse:
        codigo = STATUS_POR_ERRO.get(type(erro), status.HTTP_400_BAD_REQUEST)
        cabecalhos = (
            {"WWW-Authenticate": "Bearer"}
            if codigo == status.HTTP_401_UNAUTHORIZED
            else None
        )
        return JSONResponse(
            status_code=codigo, content={"detail": str(erro)}, headers=cabecalhos
        )
