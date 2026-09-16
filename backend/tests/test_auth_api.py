from fastapi.testclient import TestClient
from sqlalchemy import select

from conftest import TestingSession
from app.core.seguridad import hash_password
from app.main import app
from app.models.usuario import Usuario


client = TestClient(app)


def _register(email="ana@example.com", password="clave-segura-123", nombre="Ana", rol=None):
    body = {"email": email, "nombre": nombre, "password": password}
    if rol is not None:
        body["rol"] = rol
    return client.post("/api/auth/register", json=body)


def _login(email, password):
    return client.post(
        "/api/auth/login", data={"username": email, "password": password}
    )


def test_registro_login_y_perfil():
    assert _register().status_code == 201

    login = _login("ana@example.com", "clave-segura-123")
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ana@example.com"
    assert me.json()["rol"] == "cliente"


def test_registro_duplicado_y_validaciones():
    assert _register(email="dupe@example.com").status_code == 201
    assert _register(email="dupe@example.com").status_code == 409
    assert _register(email="corta@example.com", password="abc").status_code == 422
    assert _register(email="rol@example.com", rol="super").status_code == 422
    assert _register(email="no-email").status_code == 422


def test_login_rechaza_credenciales_malas():
    _register(email="luis@example.com")
    assert _login("luis@example.com", "otra-clave-123").status_code == 401
    assert _login("nadie@example.com", "clave-segura-123").status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get(
        "/api/auth/me", headers={"Authorization": "Bearer invalido"}
    ).status_code == 401


def _admin_token():
    db = TestingSession()
    if not db.scalar(select(Usuario).where(Usuario.email == "admin@example.com")):
        db.add(
            Usuario(
                email="admin@example.com",
                nombre="Admin",
                password_hash=hash_password("admin-seguro-123"),
                rol="admin",
            )
        )
        db.commit()
    db.close()
    return _login("admin@example.com", "admin-seguro-123").json()["access_token"]


def test_admin_gestiona_usuarios_y_no_admin_es_rechazado():
    _register(email="comun@example.com")
    user_token = _login("comun@example.com", "clave-segura-123").json()["access_token"]
    assert (
        client.get("/api/auth/usuarios", headers={"Authorization": f"Bearer {user_token}"}).status_code
        == 403
    )

    admin = {"Authorization": f"Bearer {_admin_token()}"}
    listado = client.get("/api/auth/usuarios", headers=admin)
    assert listado.status_code == 200
    assert any(u["email"] == "comun@example.com" for u in listado.json())

    comun_id = next(u["id"] for u in listado.json() if u["email"] == "comun@example.com")
    cambio = client.patch(
        f"/api/auth/usuarios/{comun_id}", json={"rol": "consultor"}, headers=admin
    )
    assert cambio.status_code == 200
    assert cambio.json()["rol"] == "consultor"
    assert (
        client.patch(f"/api/auth/usuarios/{comun_id}", json={"rol": "raro"}, headers=admin).status_code
        == 422
    )

    assert client.delete(f"/api/auth/usuarios/{comun_id}", headers=admin).status_code == 204
    assert (
        client.delete(f"/api/auth/usuarios/{comun_id}", headers=admin).status_code == 404
    )

    admin_id = next(u["id"] for u in client.get("/api/auth/usuarios", headers=admin).json() if u["email"] == "admin@example.com")
    assert client.delete(f"/api/auth/usuarios/{admin_id}", headers=admin).status_code == 422
