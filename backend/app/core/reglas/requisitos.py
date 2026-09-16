import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"

with open(DATA_PATH / "requisitos_por_autoridad.json", encoding="utf-8") as archivo:
    REQUISITOS_POR_AUTORIDAD = json.load(archivo)


def obtener_requisitos(sigla_autoridad: str) -> dict:
    requisitos = REQUISITOS_POR_AUTORIDAD.get(sigla_autoridad)
    if requisitos is None:
        return {
            "autoridad": sigla_autoridad,
            "anexos": [],
            "requiere_revision": True,
            "error": "autoridad_sin_requisitos_configurados",
        }

    return {
        "autoridad": requisitos["autoridad"],
        "anexos": requisitos["anexos"],
        "requiere_revision": False,
    }
