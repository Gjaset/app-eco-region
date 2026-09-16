"""Guardarraíles del agente IA: funciones puras, sin red ni estado.

El filtro por palabras clave es la primera capa (barata y determinista);
el system prompt del endpoint es la segunda. Así las preguntas fuera de
tema se rechazan sin gastar tokens en Nvidia NIM.
"""

from __future__ import annotations

import re
import unicodedata

SENALES_TEMA = frozenset({
    "car", "sda", "corpoboyaca", "permiso", "tala", "poda", "traslado",
    "aprovechamiento", "tramite", "radicar", "radicacion", "radicado",
    "requisito", "anexo", "fun", "formato unico", "silvicultural",
    "forestal", "flora", "veda", "inventario", "predio", "secretaria",
    "ambiente", "ambiental", "boyaca", "cundinamarca", "bogota",
    "corporacion", "fgr", "salvoconducto", "compensacion", "expediente",
    "resolucion", "solicitar", "solicitud",
})

RECHAZO_AMABLE = (
    "Solo puedo ayudarte con permisos y requisitos forestales ante "
    "la CAR, la SDA o Corpoboyacá. ¿Sobre cuál entidad es tu consulta?"
)


def normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFD", (texto or "").lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", sin_tildes)).strip()


def necesita_rechazo(pregunta: str) -> bool:
    """True si la pregunta no contiene ninguna señal del tema permitido."""
    texto = normalizar(pregunta)
    if not texto:
        return True
    return not any(senal in texto for senal in SENALES_TEMA)


def detectar_entidad(pregunta: str) -> str:
    """Devuelve 'CAR' | 'SDA' | 'CORPOBOYACA' o '' si no hay entidad clara."""
    texto = normalizar(pregunta)
    if "corpoboyaca" in texto or "boyaca" in texto:
        return "CORPOBOYACA"
    if "sda" in texto or "secretaria" in texto or "distrital" in texto:
        return "SDA"
    if re.search(r"\bcar\b", texto):
        return "CAR"
    return ""
