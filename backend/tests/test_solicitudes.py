import io
import zipfile

from fastapi.testclient import TestClient

from conftest import TestingSession
from app.core.seguridad import hash_password
from app.main import app
from app.models.usuario import Usuario


client = TestClient(app)


def _register(email, rol="cliente"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "nombre": email.split("@")[0], "password": "clave-segura-123", "rol": rol},
    )


def _token(email):
    return client.post(
        "/api/auth/login", data={"username": email, "password": "clave-segura-123"}
    ).json()["access_token"]


def _auth(email):
    return {"Authorization": f"Bearer {_token(email)}"}


def _exportar(headers, nombre="Predio Demo"):
    return client.post(
        "/api/formulario/fun/exportar-pdf",
        json={
            "tipoSolicitud": "nueva",
            "tipoPersona": "natural",
            "nombreRazonSocial": nombre,
            "tipoIdentificacion": "CC",
            "numeroIdentificacion": "12345678",
            "calidadPredio": "propietario",
            "tipoPredio": "rural",
            "costoProyecto": "1500000",
            "costoProyectoLetras": "un millón quinientos mil pesos",
            "modoAdquirirDerecho": "propiedad",
            "categoriaProducto": "maderables",
            "metodoAprovechamiento": "manual",
            "nombrePredio": nombre,
            "superficieHa": "12,5",
            "direccionPredio": "Vereda El Centro",
            "urbanoRural": "rural",
            "departamento": "Cundinamarca",
            "municipio": "Bogotá D.C.",
            "nombreFirmante": nombre,
            "especies": [
                {
                    "cantidad": "10",
                    "nombreComun": "Eucalipto",
                    "nombreCientifico": "Eucalyptus globulus",
                }
            ],
        },
        headers=headers,
    )


def test_exportar_guarda_copia_y_mias_la_lista_en_orden():
    _register("sol1@example.com")
    headers = _auth("sol1@example.com")
    assert _exportar(headers, "Predio Uno").status_code == 200
    assert _exportar(headers, "Predio Dos").status_code == 200

    mias = client.get("/api/solicitudes/mias", headers=headers)
    assert mias.status_code == 200
    assert len(mias.json()) == 2
    # Orden descendente por fecha
    assert mias.json()[0]["creado_en"] >= mias.json()[1]["creado_en"]
    assert mias.json()[0]["usuario_email"] == "sol1@example.com"
    assert all(s["nombre_archivo"].endswith(".pdf") for s in mias.json())


def test_exportar_sin_login_es_401_y_mias_tambien():
    assert client.post("/api/formulario/fun/exportar-pdf", json={}).status_code == 401
    assert client.get("/api/solicitudes/mias").status_code == 401


def test_admin_ve_todo_filtra_y_descarga_zip():
    _register("soladmin@example.com", rol="admin")
    _register("soluser@example.com")
    admin = _auth("soladmin@example.com")
    user = _auth("soluser@example.com")
    _exportar(user, "Predio Usuario")

    todas = client.get("/api/solicitudes", headers=admin)
    assert todas.status_code == 200
    assert any(s["usuario_email"] == "soluser@example.com" for s in todas.json())

    uid = next(s["usuario_id"] for s in todas.json() if s["usuario_email"] == "soluser@example.com")
    filtradas = client.get(f"/api/solicitudes?usuario_id={uid}", headers=admin)
    assert filtradas.status_code == 200
    assert {s["usuario_email"] for s in filtradas.json()} == {"soluser@example.com"}

    # No-admin no puede listar todo
    assert client.get("/api/solicitudes", headers=user).status_code == 403

    ids = ",".join(str(s["id"]) for s in filtradas.json())
    descarga = client.get(f"/api/solicitudes/descargar-zip?ids={ids}", headers=admin)
    assert descarga.status_code == 200
    assert descarga.headers["content-type"] == "application/zip"
    assert "Content-Disposition" in descarga.headers
    with zipfile.ZipFile(io.BytesIO(descarga.content)) as zf:
        assert len(zf.namelist()) == len(filtradas.json())


def test_usuario_no_descarga_lo_ajeno_pero_si_lo_propio():
    _register("dueno@example.com")
    _register("ajeno@example.com")
    dueno = _auth("dueno@example.com")
    ajeno = _auth("ajeno@example.com")
    _exportar(dueno, "Predio Dueño")

    ajenas = client.get("/api/solicitudes/mias", headers=ajeno).json()
    assert ajenas == []
    propias = client.get("/api/solicitudes/mias", headers=dueno).json()
    sid = propias[0]["id"]

    assert client.get(f"/api/solicitudes/{sid}/descargar", headers=ajeno).status_code == 403
    ok = client.get(f"/api/solicitudes/{sid}/descargar", headers=dueno)
    assert ok.status_code == 200
    assert ok.headers["content-type"] == "application/pdf"

    assert client.get(f"/api/solicitudes/descargar-zip?ids={sid}", headers=ajeno).status_code == 403
    assert client.get("/api/solicitudes/descargar-zip?ids=999999", headers=dueno).status_code == 404


def test_admin_directo_en_db_y_staff_ve_tramites():
    db = TestingSession()
    db.add(
        Usuario(
            email="jefe@example.com",
            nombre="Jefe",
            password_hash=hash_password("clave-segura-123"),
            rol="admin",
        )
    )
    db.commit()
    db.close()
    headers = _auth("jefe@example.com")
    assert client.get("/api/solicitudes", headers=headers).status_code == 200


def test_subir_documento_lo_guarda_y_lista():
    _register("subir@example.com")
    headers = _auth("subir@example.com")

    contenido = b"contenido-de-prueba-xlsx"
    resp = client.post(
        "/api/solicitudes/subir",
        headers=headers,
        data={"tipo": "f1"},
        files={"archivo": ("ficha_f1.xlsx", contenido, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tipo"] == "f1"
    assert body["nombre_archivo"].endswith(".xlsx")

    mias = client.get("/api/solicitudes/mias", headers=headers).json()
    assert any(s["tipo"] == "f1" for s in mias)

    # Descarga del archivo subido
    sid = body["id"]
    dl = client.get(f"/api/solicitudes/{sid}/descargar", headers=headers)
    assert dl.status_code == 200
    assert dl.content == contenido


def test_subir_exige_login_y_tipo_valido():
    _register("subir2@example.com")
    headers = _auth("subir2@example.com")
    resp = client.post(
        "/api/solicitudes/subir",
        data={"tipo": "otro-desconocido"},
        files={"archivo": ("a.xlsx", b"x", "application/octet-stream")},
    )
    # Sin token -> 401 (no se registra el tipo inválido primero)
    sin_token = client.post(
        "/api/solicitudes/subir",
        data={"tipo": "f1"},
        files={"archivo": ("a.xlsx", b"x", "application/octet-stream")},
    )
    assert sin_token.status_code == 401
    resp_auth = client.post(
        "/api/solicitudes/subir",
        headers=headers,
        data={"tipo": "desconocido"},
        files={"archivo": ("a.xlsx", b"x", "application/octet-stream")},
    )
    assert resp_auth.status_code == 422
