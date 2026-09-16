"""Fichas de conocimiento por autoridad para el agente IA.

Los documentos (requisitos, manuales) viven como JSON estructurados en
`backend/data/` y se cargan en memoria una sola vez. Por cada pregunta solo
se inyecta la ficha de la entidad detectada —no todo el corpus— para
mantener el prompt corto y barato.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.config import settings
from app.core.ia.guardarrailes import detectar_entidad

NOMBRE_ENTIDAD = {
    "CAR": "Corporación Autónoma Regional de Cundinamarca (CAR)",
    "SDA": "Secretaría Distrital de Ambiente (SDA)",
    "CORPOBOYACA": "Corporación Autónoma Regional de Boyacá (Corpoboyacá)",
}


def _ruta_requisitos() -> Path | None:
    candidatos = [
        Path(__file__).resolve().parents[3] / "data" / "requisitos_por_autoridad.json",
        Path(settings.DATA_PATH) / "requisitos_por_autoridad.json",
    ]
    for ruta in candidatos:
        if ruta.is_file():
            return ruta
    return None


@lru_cache(maxsize=1)
def cargar_requisitos() -> dict:
    ruta = _ruta_requisitos()
    if ruta is None:
        return {}
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def entidades_disponibles() -> list[str]:
    return [sigla for sigla in ("CAR", "SDA", "CORPOBOYACA") if sigla in cargar_requisitos()]


def _ficha_entidad(sigla: str) -> str:
    datos = cargar_requisitos().get(sigla, {})
    nombre = datos.get("autoridad", NOMBRE_ENTIDAD.get(sigla, sigla))
    anexos = datos.get("anexos") or []
    lineas = [f"[FICHA {sigla} — fuente: requisitos_por_autoridad.json]",
              f"Entidad: {nombre}"]
    if anexos:
        lineas.append("Anexos exigidos:")
        lineas.extend(f"- {anexo}" for anexo in anexos)
    return "\n".join(lineas)


def ficha_para(pregunta: str) -> str:
    """Ficha de la entidad detectada, o resumen de las tres si es ambigua."""
    entidad = detectar_entidad(pregunta)
    if entidad and entidad in cargar_requisitos():
        return _ficha_entidad(entidad)
    fichas = [_ficha_entidad(sigla) for sigla in entidades_disponibles()]
    return "\n\n".join(fichas) if fichas else ""
