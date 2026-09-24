"""Casos de uso de avaliações.

Aqui mora a integração entre os dois bancos: a avaliação só entra no MongoDB
se o palestrante existir no PostgreSQL. A regra é do negócio, não do endpoint.
"""

from dataclasses import dataclass

from app.domain.entities.avaliacao import Avaliacao, EstatisticasDeAvaliacao
from app.domain.errors import RecursoNaoEncontrado
from app.domain.ports.repositorios import AvaliacaoRepositorio, PalestranteRepositorio


@dataclass
class _ExigePalestrante:
    palestrantes: PalestranteRepositorio

    def _validar(self, palestrante_id: int) -> None:
        if not self.palestrantes.obter(palestrante_id):
            raise RecursoNaoEncontrado("Palestrante não encontrado")


@dataclass
class CriarAvaliacao(_ExigePalestrante):
    avaliacoes: AvaliacaoRepositorio

    async def executar(self, avaliacao: Avaliacao) -> Avaliacao:
        self._validar(avaliacao.palestrante_id)
        return await self.avaliacoes.criar(avaliacao)


@dataclass
class ListarAvaliacoes:
    avaliacoes: AvaliacaoRepositorio

    async def executar(self, palestrante_id: int) -> list[Avaliacao]:
        return await self.avaliacoes.listar_por_palestrante(palestrante_id)


@dataclass
class ObterEstatisticas(_ExigePalestrante):
    avaliacoes: AvaliacaoRepositorio

    async def executar(self, palestrante_id: int) -> EstatisticasDeAvaliacao:
        self._validar(palestrante_id)
        contagem = await self.avaliacoes.contar_por_nota(palestrante_id)
        return EstatisticasDeAvaliacao.de_contagem(palestrante_id, contagem)
