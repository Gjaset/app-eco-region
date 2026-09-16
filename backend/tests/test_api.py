from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


BASE_FORM = {
    "titular": {
        "nombre": "ECO REGIÓN SAS BIC",
        "nit": "900000000-1",
        "representante_legal": "Persona Responsable",
        "direccion": "Bogotá",
    },
    "predio": {
        "nombre": "Predio Demo",
        "municipio": "Bogotá D.C.",
        "vereda": "Vereda Demo",
        "latitud": "4.6639",
        "longitud": "-74.0721",
    },
    "aprovechamiento": {
        "tipo": "leña para consumo propio",
        "justificacion": "Consumo propio",
        "volumen_total": 1.5,
        "unidad": "m3",
    },
    "especies": [{"nombre": "pino", "cantidad": 2, "diametro_cm": 20}],
}


def test_normalizar_endpoint_devuelve_checklist():
    response = client.post("/api/formulario/normalizar", json=BASE_FORM)

    assert response.status_code == 200
    resultado = response.json()
    assert resultado["autoridad"]["sigla"] == "SDA"
    assert resultado["requisitos"]["anexos"]
    assert resultado["listo_para_generar"] is True


def test_normalizar_endpoint_bloquea_coordenada_fuera_de_colombia():
    formulario = {
        **BASE_FORM,
        "predio": {**BASE_FORM["predio"], "latitud": "40.7128"},
    }

    response = client.post("/api/formulario/normalizar", json=formulario)

    assert response.status_code == 200
    assert response.json()["listo_para_generar"] is False


def test_normalizar_endpoint_permite_confirmacion_explicita():
    formulario = {
        **BASE_FORM,
        "predio": {**BASE_FORM["predio"], "latitud": "40.7128"},
        "confirmar_revision": True,
    }

    response = client.post("/api/formulario/normalizar", json=formulario)

    assert response.status_code == 200
    resultado = response.json()
    assert resultado["requiere_revision"] is True
    assert resultado["revision_confirmada"] is True
    assert resultado["listo_para_generar"] is True


def test_normalizar_rechaza_autoridad_no_disponible():
    formulario = {**BASE_FORM, "autoridad_seleccionada": "NO_EXISTE"}

    response = client.post("/api/formulario/normalizar", json=formulario)

    assert response.status_code == 422
    assert "no está disponible" in response.json()["detail"]


def test_asistente_usa_fallback_sin_api_key(monkeypatch):
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "")

    response = client.post(
        "/api/ia/chat",
        json={"messages": [{"role": "user", "content": "¿Qué debo revisar?"}]},
    )

    assert response.status_code == 200
    assert response.json()["fallback"] is True
    assert response.json()["reply"]


def test_draft_rejects_stale_version():
    draft_id = "test-version-conflict"
    first = client.put(
        f"/api/formulario/drafts/{draft_id}",
        json={"version": 0, "data": {"titular": {"nombre": "uno"}}},
    )
    assert first.status_code == 200
    assert first.json()["version"] == 1

    stale = client.put(
        f"/api/formulario/drafts/{draft_id}",
        json={"version": 0, "data": {"titular": {"nombre": "dos"}}},
    )
    assert stale.status_code == 409

    current = client.get(f"/api/formulario/drafts/{draft_id}")
    assert current.status_code == 200
    assert current.json()["data"]["titular"]["nombre"] == "uno"
