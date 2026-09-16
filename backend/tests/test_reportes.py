"""Endpoints de reportes para el panel admin."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register(email, rol="admin"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "nombre": email.split("@")[0], "password": "clave-segura-123", "rol": rol},
    )


def _auth(email):
    token = client.post(
        "/api/auth/login", data={"username": email, "password": "clave-segura-123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_reportes_exige_admin():
    assert client.get("/api/reportes/resumen").status_code == 401
    _register("reporte@example.com", rol="cliente")
    headers = _auth("reporte@example.com")
    assert client.get("/api/reportes/resumen", headers=headers).status_code == 403


def test_reportes_admin_devuelve_resumen():
    _register("adminbh@example.com", rol="admin")
    headers = _auth("adminbh@example.com")

    resp = client.get("/api/reportes/resumen", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "totales" in body
    assert "por_tipo" in body
    assert "por_mes" in body
    assert "top_usuarios" in body
    assert "actividad_reciente" in body
    assert isinstance(body["totales"]["solicitudes"], int)
    assert isinstance(body["totales"]["usuarios"], int)


def test_reportes_detalle_con_filtros():
    _register("detailadmin@example.com", rol="admin")
    headers = _auth("detailadmin@example.com")

    # Sin filtros: devuelve estructura correcta aunque no haya datos
    resp = client.get("/api/reportes/detalle", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "registros" in body
    assert "total" in body
    assert body["total"] == len(body["registros"])

    # Filtro por tipo (vacío -> total 0 en SQLite sin datos)
    resp2 = client.get("/api/reportes/detalle", params={"tipo": "f1"}, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["total"] == 0

    # Filtro por fecha (formato válido)
    resp3 = client.get("/api/reportes/detalle", params={"fecha_desde": "2026-01-01", "fecha_hasta": "2026-12-31"}, headers=headers)
    assert resp3.status_code == 200