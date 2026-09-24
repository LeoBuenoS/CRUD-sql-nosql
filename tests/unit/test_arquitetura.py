"""Fitness function da arquitetura.

A regra da Clean Architecture ("a dependência aponta para dentro") só vale se
for verificada. Estes testes leem os imports de cada módulo e falham se alguém
furar a camada — o CI passa a segurar a decisão do ADR-0002, não a boa vontade
de quem revisa.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2] / "app"

FRAMEWORKS = (
    "fastapi",
    "starlette",
    "sqlalchemy",
    "motor",
    "pymongo",
    "jwt",
    "bcrypt",
    "pydantic",
)

# camada -> pacotes do projeto que ela NÃO pode importar
PROIBIDOS_INTERNOS = {
    "domain": ("app.application", "app.infrastructure", "app.interfaces"),
    "application": ("app.infrastructure", "app.interfaces"),
    "infrastructure": ("app.application", "app.interfaces"),
}


def _modulos(camada: str) -> list[Path]:
    return sorted((RAIZ / camada).rglob("*.py"))


def _imports(arquivo: Path) -> list[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: list[str] = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes += [alias.name for alias in no.names]
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            nomes.append(no.module)
    return nomes


def _id(arquivo: Path) -> str:
    return str(arquivo.relative_to(RAIZ))


@pytest.mark.parametrize(
    "arquivo", _modulos("domain") + _modulos("application"), ids=_id
)
def test_nucleo_nao_conhece_framework(arquivo):
    """Domínio e aplicação não importam FastAPI, SQLAlchemy, Motor, JWT..."""
    for importado in _imports(arquivo):
        raiz = importado.split(".")[0]
        assert raiz not in FRAMEWORKS, f"{arquivo.name} importa {importado}"


@pytest.mark.parametrize(
    "arquivo",
    _modulos("domain") + _modulos("application") + _modulos("infrastructure"),
    ids=_id,
)
def test_dependencia_aponta_para_dentro(arquivo):
    camada = arquivo.relative_to(RAIZ).parts[0]
    for importado in _imports(arquivo):
        for proibido in PROIBIDOS_INTERNOS[camada]:
            assert not importado.startswith(
                proibido
            ), f"{camada}/{arquivo.name} importa {importado}"


def test_infraestrutura_so_entra_pelo_composition_root():
    """Router nenhum fala com adaptador concreto: quem amarra é o deps.py."""
    for arquivo in _modulos("interfaces"):
        if arquivo.name == "deps.py":
            continue
        for importado in _imports(arquivo):
            assert not importado.startswith(
                "app.infrastructure"
            ), f"{arquivo.name} importa {importado} — use app/interfaces/http/deps.py"
