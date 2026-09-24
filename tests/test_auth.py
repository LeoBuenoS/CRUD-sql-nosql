from app.core.config import settings
from app.core.security import criar_access_token

from tests.conftest import CREDENCIAIS
from tests.test_palestrantes import BASE


def _token(client) -> str:
    client.post("/auth/registrar", json=CREDENCIAIS)
    r = client.post(
        "/auth/token",
        data={"username": CREDENCIAIS["email"], "password": CREDENCIAIS["senha"]},
    )
    return r.json()["access_token"]


def test_registrar_e_logar(anon_client):
    r = anon_client.post("/auth/registrar", json=CREDENCIAIS)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == CREDENCIAIS["email"]
    assert "senha" not in body and "senha_hash" not in body

    r = anon_client.post(
        "/auth/token",
        data={"username": CREDENCIAIS["email"], "password": CREDENCIAIS["senha"]},
    )
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_email_duplicado_retorna_409(anon_client):
    anon_client.post("/auth/registrar", json=CREDENCIAIS)
    assert anon_client.post("/auth/registrar", json=CREDENCIAIS).status_code == 409


def test_senha_curta_retorna_422(anon_client):
    dados = {"email": "outro@exemplo.com", "senha": "curta"}
    assert anon_client.post("/auth/registrar", json=dados).status_code == 422


def test_senha_errada_retorna_401(anon_client):
    anon_client.post("/auth/registrar", json=CREDENCIAIS)
    r = anon_client.post(
        "/auth/token",
        data={"username": CREDENCIAIS["email"], "password": "senha-errada"},
    )
    assert r.status_code == 401


def test_eu_devolve_o_usuario_do_token(anon_client):
    token = _token(anon_client)
    r = anon_client.get("/auth/eu", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == CREDENCIAIS["email"]


def test_token_invalido_retorna_401(anon_client):
    r = anon_client.get("/auth/eu", headers={"Authorization": "Bearer nao-e-um-jwt"})
    assert r.status_code == 401


def test_leitura_e_publica(anon_client, client):
    # `client` cria um palestrante autenticado; `anon_client` lê sem token.
    pid = client.post("/palestrantes", data=BASE).json()["id"]
    del anon_client.headers["Authorization"]

    assert anon_client.get("/palestrantes").status_code == 200
    assert anon_client.get(f"/palestrantes/{pid}").status_code == 200
    assert anon_client.get(f"/avaliacoes/{pid}").status_code == 200


def test_escrita_sem_token_retorna_401(anon_client, client):
    pid = client.post("/palestrantes", data=BASE).json()["id"]
    del anon_client.headers["Authorization"]

    assert anon_client.post("/palestrantes", data=BASE).status_code == 401
    assert anon_client.put(f"/palestrantes/{pid}", data=BASE).status_code == 401
    assert anon_client.delete(f"/palestrantes/{pid}").status_code == 401

    avaliacao = {"palestrante_id": pid, "autor": "Anon", "nota": 5}
    assert anon_client.post("/avaliacoes", json=avaliacao).status_code == 401


def test_token_expirado_retorna_401(anon_client, monkeypatch):
    anon_client.post("/auth/registrar", json=CREDENCIAIS)
    monkeypatch.setattr(settings, "jwt_expire_minutes", -1)
    token = criar_access_token(CREDENCIAIS["email"])

    r = anon_client.get("/auth/eu", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
