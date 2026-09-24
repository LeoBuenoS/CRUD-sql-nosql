"""Portas de serviços técnicos (arquivos, hash de senha, token).

O domínio fala de "guardar um arquivo" e "emitir um token", não de
filesystem, bcrypt ou PyJWT — essas escolhas ficam na infraestrutura.
"""

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass
class ArquivoBinario:
    """Arquivo recebido, já desacoplado do UploadFile do FastAPI."""

    nome_original: str
    conteudo: BinaryIO


class ArmazenamentoDeArquivos(Protocol):
    def salvar(self, arquivo: ArquivoBinario) -> str:
        """Grava o binário e devolve o nome do arquivo armazenado."""
        ...

    def remover(self, nome_arquivo: str | None) -> None: ...


class HashDeSenha(Protocol):
    def gerar(self, senha: str) -> str: ...

    def verificar(self, senha: str, senha_hash: str) -> bool: ...


class EmissorDeToken(Protocol):
    def emitir(self, sujeito: str) -> str: ...

    def ler(self, token: str) -> str | None:
        """Devolve o sujeito do token, ou None se inválido/expirado."""
        ...
