from zipfile import ZipFile

from app.core.generacion.documento_word import generar_documento


def test_generar_documento_usa_plantilla_disponible(tmp_path):
    datos = {
        "titular": {
            "nombre": "ECO REGIÓN SAS BIC",
            "nit": "900000000-1",
            "representante_legal": "Persona Responsable",
            "direccion": "Bogotá",
        },
        "predio": {
            "nombre": "Predio Demo",
            "vereda": "Vereda Demo",
        },
        "municipio": {
            "nombre_oficial": "Bogotá D.C.",
            "departamento": "Cundinamarca",
        },
        "latitud": {"valor_decimal": 4.6639},
        "longitud": {"valor_decimal": -74.0721},
        "tipo_aprovechamiento": {"categoria": "Aprovechamiento Doméstico"},
        "aprovechamiento": {
            "justificacion": "Consumo propio",
            "volumen_total": 1.5,
        },
        "autoridad": {
            "nombre": "Secretaría Distrital de Ambiente",
            "sigla": "SDA",
        },
        "especies": [],
    }

    documento = generar_documento(datos)

    output = tmp_path / "aprovechamiento.docx"
    output.write_bytes(documento)
    with ZipFile(output) as archivo:
        contenido = archivo.read("word/document.xml").decode("utf-8")

    assert "ECO REGIÓN SAS BIC" in contenido
    assert "{{" not in contenido