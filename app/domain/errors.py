"""Erros do domínio.

São independentes de HTTP: quem traduz para status code é a camada de
interface (app/interfaces/http/errors.py). Assim o mesmo caso de uso serve
para uma API REST, uma CLI ou um worker.
"""


class ErroDeDominio(Exception):
    """Raiz de todos os erros de negócio."""


class RecursoNaoEncontrado(ErroDeDominio):
    """A entidade pedida não existe."""


class ConflitoDeDados(ErroDeDominio):
    """Violação de unicidade (ex.: e-mail já cadastrado)."""


class DadosInvalidos(ErroDeDominio):
    """Regra de negócio violada (ex.: nota fora da faixa, arquivo não suportado)."""


class CredenciaisInvalidas(ErroDeDominio):
    """Usuário inexistente, senha errada ou token inválido/expirado."""
