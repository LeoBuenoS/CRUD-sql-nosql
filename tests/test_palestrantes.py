import io

BASE = {
    "nome": "Ada Lovelace",
    "qualificacao": "Matemática",
    "experiencia": "10",
    "data_palestra": "2025-09-01",
    "hora_palestra": "14:30:00",
    "local": "Auditório 1",
}


def _fake_image() -> tuple:
    # PNG mínimo válido (assinatura) só para exercitar o upload.
    conteudo = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    return ("foto", ("palestrante.png", io.BytesIO(conteudo), "image/png"))


def test_criar_sem_foto(client):
    r = client.post("/palestrantes", data=BASE)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Ada Lovelace"
    assert body["foto"] is None


def test_criar_com_foto(client):
    r = client.post("/palestrantes", data=BASE, files=[_fake_image()])
    assert r.status_code == 201
    body = r.json()
    assert body["foto"] is not None
    assert body["foto_url"].endswith(body["foto"])


def test_extensao_invalida_retorna_400(client):
    arquivo = ("foto", ("virus.txt", io.BytesIO(b"nope"), "text/plain"))
    r = client.post("/palestrantes", data=BASE, files=[arquivo])
    assert r.status_code == 400


def test_detalhar_e_remover(client):
    criado = client.post("/palestrantes", data=BASE).json()
    pid = criado["id"]
    assert client.get(f"/palestrantes/{pid}").status_code == 200
    assert client.delete(f"/palestrantes/{pid}").status_code == 204
    assert client.get(f"/palestrantes/{pid}").status_code == 404
