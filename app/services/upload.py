"""
Serviço de upload de arquivos.

Tradução do ProcessaUploadedFile() do controller .NET:
- .NET salvava em wwwroot/Uploads com nome  Guid + "_" + FileName
- aqui salvamos em  static/uploads  com nome  uuid4 + extensão original
O binário vai para o disco (volume); o banco guarda só o nome do arquivo.
"""
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIR = Path("static/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def save_upload(file: UploadFile) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extensão não permitida: {ext or '(sem extensão)'}")

    nome_arquivo = f"{uuid.uuid4().hex}{ext}"
    destino = UPLOAD_DIR / nome_arquivo
    with destino.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return nome_arquivo


def delete_upload(nome_arquivo: str | None) -> None:
    """Remove o arquivo do disco. Equivale ao System.IO.File.Delete do .NET."""
    if not nome_arquivo:
        return
    caminho = UPLOAD_DIR / nome_arquivo
    if caminho.exists():
        caminho.unlink()
