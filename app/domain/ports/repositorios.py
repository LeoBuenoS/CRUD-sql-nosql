"""Portas de persistência.

O domínio declara o que precisa; a infraestrutura implementa (SQLAlchemy,
Motor). São Protocols: o adaptador não precisa herdar de nada, basta ter a
assinatura — e os testes passam um fake em memória.
"""

from typing import Protocol

from app.domain.entities.avaliacao import Avaliacao
from app.domain.entities.palestrante import Palestrante
from app.domain.entities.usuario import Usuario


class PalestranteRepositorio(Protocol):
    def listar(
        self, busca: str | None = None, pular: int = 0, limite: int = 50
    ) -> list[Palestrante]: ...

    def obter(self, palestrante_id: int) -> Palestrante | None: ...

    def criar(self, palestrante: Palestrante) -> Palestrante: ...

    def atualizar(self, palestrante: Palestrante) -> Palestrante: ...

    def remover(self, palestrante_id: int) -> None: ...


class AvaliacaoRepositorio(Protocol):
    async def listar_por_palestrante(self, palestrante_id: int) -> list[Avaliacao]: ...

    async def criar(self, avaliacao: Avaliacao) -> Avaliacao: ...

    async def contar_por_nota(self, palestrante_id: int) -> dict[int, int]: ...


class UsuarioRepositorio(Protocol):
    def obter_por_email(self, email: str) -> Usuario | None: ...

    def criar(self, usuario: Usuario) -> Usuario: ...
