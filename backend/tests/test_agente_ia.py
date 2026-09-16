"""Agente IA con candado temático CAR/SDA/Corpoboyacá."""

import httpx
from fastapi.testclient import TestClient

from app.config import settings
from app.core.ia.guardarrailes import RECHAZO_AMABLE, detectar_entidad, necesita_rechazo
from app.main import app

client = TestClient(app)


def test_fuera_de_tema_se_rechaza_sin_llamar_a_nim(monkeypatch):
    llamadas = []
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "test-key")

    class Espia:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            llamadas.append(kwargs)
            raise AssertionError("NIM no debe llamarse fuera de tema")

    monkeypatch.setattr(httpx, "AsyncClient", Espia)
    response = client.post("/api/ia/agente", json={"pregunta": "¿Quién ganó el partido ayer?"})
    assert response.status_code == 200
    assert response.json()["reply"] == RECHAZO_AMABLE
    assert llamadas == []


def test_sin_api_key_devuelve_fallback(monkeypatch):
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "")
    response = client.post("/api/ia/agente", json={"pregunta": "¿Qué anexos pide la CAR?"})
    assert response.status_code == 200
    body = response.json()
    assert body["fallback"] is True
    assert "CAR" in body["reply"]


def test_en_tema_consulta_a_nim_con_ficha(monkeypatch):
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "test-key")
    enviado = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "La CAR exige estos anexos…"}}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, headers=None, json=None):
            enviado["json"] = json
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    response = client.post("/api/ia/agente", json={"pregunta": "¿Qué anexos pide la CAR para tala?"})
    assert response.status_code == 200
    assert response.json()["reply"] == "La CAR exige estos anexos…"
    system = enviado["json"]["messages"][0]["content"]
    assert "CAR" in system and "Anexos exigidos" in system
    assert enviado["json"]["temperature"] == 0.2


def test_guardarrailes():
    assert necesita_rechazo("hola, ¿cómo estás?") is True
    assert necesita_rechazo("") is True
    assert necesita_rechazo("Requisitos SDA para poda") is False
    assert detectar_entidad("corpoboyacá exige plano") == "CORPOBOYACA"
    assert detectar_entidad("secretaría distrital") == "SDA"
    assert detectar_entidad("permiso de la car") == "CAR"
    assert detectar_entidad("quiero un permiso") == ""
