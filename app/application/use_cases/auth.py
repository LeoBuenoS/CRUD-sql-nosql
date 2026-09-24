"""Casos de uso de autenticação."""

from dataclasses import dataclass

from app.domain.entities.usuario import SENHA_MINIMA, Usuario
from app.domain.errors import ConflitoDeDados, CredenciaisInvalidas, DadosInvalidos
from app.domain.ports.repositorios import UsuarioRepositorio
from app.domain.ports.servicos import EmissorDeToken, HashDeSenha


@dataclass
class RegistrarUsuario:
    repositorio: UsuarioRepositorio
    hash_de_senha: HashDeSenha

    def executar(self, email: str, senha: str) -> Usuario:
        if len(senha) < SENHA_MINIMA:
            raise DadosInvalidos(f"senha deve ter ao menos {SENHA_MINIMA} caracteres")
        if self.repositorio.obter_por_email(email):
            raise ConflitoDeDados("E-mail já cadastrado")
        return self.repositorio.criar(
            Usuario(email=email, senha_hash=self.hash_de_senha.gerar(senha))
        )


@dataclass
class AutenticarUsuario:
    repositorio: UsuarioRepositorio
    hash_de_senha: HashDeSenha
    emissor: EmissorDeToken

    def executar(self, email: str, senha: str) -> str:
        """Devolve o access token, ou estoura CredenciaisInvalidas."""
        usuario = self.repositorio.obter_por_email(email)
        if not usuario or not self.hash_de_senha.verificar(senha, usuario.senha_hash):
            # Mesma resposta para usuário inexistente e senha errada:
            # não entrega ao atacante quais e-mails existem.
            raise CredenciaisInvalidas("Credenciais inválidas")
        return self.emissor.emitir(usuario.email)


@dataclass
class ObterUsuarioDoToken:
    repositorio: UsuarioRepositorio
    emissor: EmissorDeToken

    def executar(self, token: str) -> Usuario:
        email = self.emissor.ler(token)
        if not email:
            raise CredenciaisInvalidas("Credenciais inválidas")

        usuario = self.repositorio.obter_por_email(email)
        if not usuario:
            raise CredenciaisInvalidas("Credenciais inválidas")
        return usuario
