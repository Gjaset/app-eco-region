import io

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app


client = TestClient(app)


def _token(email="fun@example.com"):
    client.post(
        "/api/auth/register",
        json={"email": email, "nombre": "Fun", "password": "clave-segura-123"},
    )
    login = client.post(
        "/api/auth/login", data={"username": email, "password": "clave-segura-123"}
    )
    return login.json()["access_token"]


def _auth(email="fun@example.com"):
    return {"Authorization": f"Bearer {_token(email)}"}


def test_exportar_fun_pdf_devuelve_plantilla_rellena():
    response = client.post(
        "/api/formulario/fun/exportar-pdf",
        json={
            "tipoSolicitud": "nueva",
            "tipoPersona": "juridicaPrivada",
            "nombreRazonSocial": "ECO REGIÓN SAS BIC",
            "tipoIdentificacion": "NIT",
            "numeroIdentificacion": "900123456-8",
            "calidadPredio": "propietario",
            "tipoPredio": "rural",
            "costoProyecto": "1500000",
            "costoProyectoLetras": "un millón quinientos mil pesos",
            "modoAdquirirDerecho": "propiedad",
            "categoriaProducto": "maderables",
            "metodoAprovechamiento": "manual",
            "nombrePredio": "El Mirador",
            "superficieHa": "12,5",
            "direccionPredio": "Vereda El Centro",
            "urbanoRural": "rural",
            "departamento": "Cundinamarca",
            "municipio": "Bogotá D.C.",
            "nombreFirmante": "Ana Pérez",
            "especies": [
                {
                    "cantidad": "44,7",
                    "unidadMedida": "Metros cúbicos",
                    "nombreComun": "Eucalipto",
                    "nombreCientifico": "Eucalyptus Globulus",
                }
            ],
        },
        headers=_auth(),
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    doc = PdfReader(io.BytesIO(response.content))
    assert len(doc.pages) == 10


def test_exportar_fun_pdf_rechaza_borrador_incompleto():
    response = client.post("/api/formulario/fun/exportar-pdf", json={}, headers=_auth("vacio@example.com"))

    assert response.status_code == 422
    detalle = response.json()["detail"]
    assert "errores" in detalle
    assert "nombreRazonSocial" in detalle["errores"]
    assert "especies" in detalle["errores"]


def test_exportar_fun_pdf_exige_login():
    assert client.post("/api/formulario/fun/exportar-pdf", json={}).status_code == 401
