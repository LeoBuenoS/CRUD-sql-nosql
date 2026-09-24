from tests.integration.test_palestrantes_api import BASE


def _criar_palestrante(client) -> int:
    return client.post("/palestrantes", data=BASE).json()["id"]


def _avaliacao(palestrante_id: int, nota: int) -> dict:
    return {
        "palestrante_id": palestrante_id,
        "autor": "Grace Hopper",
        "nota": nota,
        "comentario": "Ótima palestra",
        "tags": ["didática"],
    }


def test_criar_avaliacao(client):
    pid = _criar_palestrante(client)
    r = client.post("/avaliacoes", json=_avaliacao(pid, 5))
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert body["nota"] == 5
    assert body["tags"] == ["didática"]


def test_avaliacao_de_palestrante_inexistente_retorna_404(client):
    assert client.post("/avaliacoes", json=_avaliacao(999, 5)).status_code == 404


def test_nota_fora_do_intervalo_retorna_422(client):
    pid = _criar_palestrante(client)
    assert client.post("/avaliacoes", json=_avaliacao(pid, 9)).status_code == 422


def test_listar_avaliacoes_do_palestrante(client):
    pid = _criar_palestrante(client)
    outro = _criar_palestrante(client)
    client.post("/avaliacoes", json=_avaliacao(pid, 4))
    client.post("/avaliacoes", json=_avaliacao(pid, 2))
    client.post("/avaliacoes", json=_avaliacao(outro, 5))

    avaliacoes = client.get(f"/avaliacoes/{pid}").json()
    assert len(avaliacoes) == 2
    assert {a["nota"] for a in avaliacoes} == {4, 2}


def test_estatisticas_agrega_as_notas(client):
    pid = _criar_palestrante(client)
    for nota in (5, 4, 3):
        client.post("/avaliacoes", json=_avaliacao(pid, nota))

    stats = client.get(f"/avaliacoes/{pid}/estatisticas").json()
    assert stats["total"] == 3
    assert stats["media"] == 4.0
    assert stats["distribuicao"] == {"1": 0, "2": 0, "3": 1, "4": 1, "5": 1}


def test_estatisticas_sem_avaliacoes(client):
    pid = _criar_palestrante(client)
    stats = client.get(f"/avaliacoes/{pid}/estatisticas").json()
    assert stats["total"] == 0
    assert stats["media"] is None
