"""Armazenamento em disco local.

Adaptador da porta ArmazenamentoDeArquivos. Trocar por S3 significa escrever
outro adaptador — o domínio e os casos de uso não mudam.
"""

import shutil
import uuid
from pathlib import Path

from app.domain.errors import DadosInvalidos
from app.domain.ports.servicos import ArquivoBinario
from app.infrastructure.config import settings

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class ArmazenamentoLocal:
    def __init__(self, diretorio: Path | None = None):
        self.diretorio = Path(diretorio or settings.upload_dir)

    def salvar(self, arquivo: ArquivoBinario) -> str:
        extensao = Path(arquivo.nome_original or "").suffix.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise DadosInvalidos(
                f"Extensão não permitida: {extensao or '(sem extensão)'}"
            )

        self.diretorio.mkdir(parents=True, exist_ok=True)
        nome_arquivo = f"{uuid.uuid4().hex}{extensao}"
        with (self.diretorio / nome_arquivo).open("wb") as destino:
            shutil.copyfileobj(arquivo.conteudo, destino)
        return nome_arquivo

    def remover(self, nome_arquivo: str | None) -> None:
        if not nome_arquivo:
            return
        caminho = self.diretorio / nome_arquivo
        if caminho.exists():
            caminho.unlink()
