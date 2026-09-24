"""Adaptadores falsos, em memória, para os testes unitários.

Implementam as mesmas portas que PostgreSQL, MongoDB, bcrypt e disco — é o
que permite testar os casos de uso sem infraestrutura nenhuma.
"""

from dataclasses import replace
from datetime import datetime, timezone

from app.domain.entities.avaliacao import Avaliacao
from app.domain.entities.palestrante import Palestrante
from app.domain.entities.usuario import Usuario
from app.domain.errors import DadosInvalidos
from app.domain.ports.servicos import ArquivoBinario


class PalestranteRepositorioFake:
    def __init__(self, iniciais: list[Palestrante] | None = None):
        self.itens: dict[int, Palestrante] = {}
        self._proximo_id = 1
        for palestrante in iniciais or []:
            self.criar(palestrante)

    def listar(self, busca=None, pular=0, limite=50) -> list[Palestrante]:
        itens = [self.itens[k] for k in sorted(self.itens)]
        if busca:
            termo = busca.lower()
            itens = [
                p for p in itens if termo in p.nome.lower() or termo in p.local.lower()
            ]
        return itens[pular : pular + limite]

    def obter(self, palestrante_id: int) -> Palestrante | None:
        return self.itens.get(palestrante_id)

    def criar(self, palestrante: Palestrante) -> Palestrante:
        novo = replace(palestrante, id=self._proximo_id)
        self.itens[novo.id] = novo
        self._proximo_id += 1
        return novo

    def atualizar(self, palestrante: Palestrante) -> Palestrante:
        self.itens[palestrante.id] = palestrante
        return palestrante

    def remover(self, palestrante_id: int) -> None:
        self.itens.pop(palestrante_id, None)


class AvaliacaoRepositorioFake:
    def __init__(self):
        self.itens: list[Avaliacao] = []

    async def listar_por_palestrante(self, palestrante_id: int) -> list[Avaliacao]:
        return [a for a in self.itens if a.palestrante_id == palestrante_id]

    async def criar(self, avaliacao: Avaliacao) -> Avaliacao:
        nova = replace(
            avaliacao,
            id=str(len(self.itens) + 1),
            criado_em=avaliacao.criado_em or datetime.now(timezone.utc),
        )
        self.itens.append(nova)
        return nova

    async def contar_por_nota(self, palestrante_id: int) -> dict[int, int]:
        contagem: dict[int, int] = {}
        for avaliacao in await self.listar_por_palestrante(palestrante_id):
            contagem[avaliacao.nota] = contagem.get(avaliacao.nota, 0) + 1
        return contagem


class UsuarioRepositorioFake:
    def __init__(self):
        self.itens: dict[str, Usuario] = {}

    def obter_por_email(self, email: str) -> Usuario | None:
        return self.itens.get(email)

    def criar(self, usuario: Usuario) -> Usuario:
        novo = replace(
            usuario, id=len(self.itens) + 1, criado_em=datetime.now(timezone.utc)
        )
        self.itens[novo.email] = novo
        return novo


class ArmazenamentoFake:
    """Guarda os "arquivos" num dict e registra o que foi removido."""

    EXTENSOES = {".jpg", ".png"}

    def __init__(self):
        self.salvos: dict[str, bytes] = {}
        self.removidos: list[str] = []

    def salvar(self, arquivo: ArquivoBinario) -> str:
        if not any(arquivo.nome_original.endswith(e) for e in self.EXTENSOES):
            raise DadosInvalidos("Extensão não permitida")
        nome = f"{len(self.salvos) + 1}-{arquivo.nome_original}"
        self.salvos[nome] = arquivo.conteudo.read()
        return nome

    def remover(self, nome_arquivo: str | None) -> None:
        if nome_arquivo:
            self.removidos.append(nome_arquivo)
            self.salvos.pop(nome_arquivo, None)


class HashDeSenhaFake:
    """Hash reversível e instantâneo — só os casos de uso estão sob teste."""

    def gerar(self, senha: str) -> str:
        return f"hash::{senha}"

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return senha_hash == self.gerar(senha)


class EmissorDeTokenFake:
    def __init__(self, valido: bool = True):
        self.valido = valido

    def emitir(self, sujeito: str) -> str:
        return f"token::{sujeito}"

    def ler(self, token: str) -> str | None:
        if not self.valido or not token.startswith("token::"):
            return None
        return token.removeprefix("token::")
