"""Casos de uso de palestrantes.

Cada classe é uma operação de negócio completa. Dependem só de portas, então
rodam em teste unitário com repositórios falsos, sem banco e sem HTTP.
"""

from dataclasses import dataclass, replace

from app.domain.entities.palestrante import Palestrante
from app.domain.errors import RecursoNaoEncontrado
from app.domain.ports.repositorios import PalestranteRepositorio
from app.domain.ports.servicos import ArmazenamentoDeArquivos, ArquivoBinario


@dataclass
class ListarPalestrantes:
    repositorio: PalestranteRepositorio

    def executar(
        self, busca: str | None = None, pular: int = 0, limite: int = 50
    ) -> list[Palestrante]:
        return self.repositorio.listar(busca=busca, pular=pular, limite=limite)


@dataclass
class ObterPalestrante:
    repositorio: PalestranteRepositorio

    def executar(self, palestrante_id: int) -> Palestrante:
        palestrante = self.repositorio.obter(palestrante_id)
        if not palestrante:
            raise RecursoNaoEncontrado("Palestrante não encontrado")
        return palestrante


@dataclass
class CriarPalestrante:
    repositorio: PalestranteRepositorio
    armazenamento: ArmazenamentoDeArquivos

    def executar(
        self, palestrante: Palestrante, foto: ArquivoBinario | None = None
    ) -> Palestrante:
        if foto:
            palestrante = palestrante.com_foto(self.armazenamento.salvar(foto))
        return self.repositorio.criar(palestrante)


@dataclass
class EditarPalestrante:
    repositorio: PalestranteRepositorio
    armazenamento: ArmazenamentoDeArquivos

    def executar(
        self,
        palestrante_id: int,
        dados: Palestrante,
        foto: ArquivoBinario | None = None,
    ) -> Palestrante:
        atual = ObterPalestrante(self.repositorio).executar(palestrante_id)

        # Sem foto nova, a imagem atual é preservada.
        novo = dados.com_foto(atual.foto)
        if foto:
            novo = novo.com_foto(self.armazenamento.salvar(foto))

        atualizado = self.repositorio.atualizar(replace(novo, id=palestrante_id))
        if foto:
            # Só apaga a antiga depois que a troca foi persistida.
            self.armazenamento.remover(atual.foto)
        return atualizado


@dataclass
class RemoverPalestrante:
    repositorio: PalestranteRepositorio
    armazenamento: ArmazenamentoDeArquivos

    def executar(self, palestrante_id: int) -> None:
        palestrante = ObterPalestrante(self.repositorio).executar(palestrante_id)
        self.repositorio.remover(palestrante_id)
        self.armazenamento.remover(palestrante.foto)
