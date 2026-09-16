"""Validación IA de formatos subidos: extrae texto y pide al LLM un dictamen
estructurado en JSON sobre si el documento está correctamente diligenciado.
"""
import json
import logging
import re
from datetime import datetime, timezone

import httpx

from app.config import settings

from .checklists import checklist_para
from .extraccion import SinTextoError, extraer_texto

logger = logging.getLogger(__name__)

SYSTEM = """Eres un revisor técnico experto en formatos de aprovechamiento forestal de \
Colombia (CAR, SDA, Corpoboyacá). Tu tarea es leer el texto de un formato y \
compararlo con una lista de verificación. Sé estricto: marca un campo como \
faltante únicamente si falta o viene vacío, no especules sobre su corrección \
legal. Responde ÚNICAMENTE con un objeto JSON válido con esta forma exacta:
{
  "apto": true | false,
  "puntaje": <entero 0-100>,
  "faltantes": [{"campo": "<nombre del campo en la checklist>", "detalle": "<por qué falta o qué contiene>"}],
  "observaciones": ["<hallazgo relevante>"],
  "resumen": "<frase corta y amable para el usuario, en español>"
}
- "apto" es true solo si no hay faltantes.
- "puntaje" refleja el porcentaje de campos completos.
- No agregues texto fuera del JSON."""


def _reparar_json(texto: str) -> str:
    """Reparaciones ligeras a JSON casi válido: comas colgantes, comillas simples
    y saltos de línea dentro de strings.

    No es un parser completo: solo corrige los errores típicos del modelo.
    """
    s = texto.strip()
    # Cortar cualquier char suelto después del último }
    ultimo = s.rfind("}")
    if ultimo != -1:
        s = s[: ultimo + 1]
    # } , ] o ] , } -> quitar la coma colgante
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    # Cadenas multilínea sin escapar: "texto\n..." -> unir (dentro de strings)
    s = re.sub(r"\n", " ", s)
    return s


def _parse_json(contento: str) -> dict:
    """Extrae el primer objeto JSON del texto; tolera cercas de código y
    errores leves de formato (trailing commas, saltos de línea en valores)."""
    texto = contento.strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        raise ValueError("La respuesta del modelo no contiene JSON")
    fragmento = match.group(0)
    try:
        return json.loads(fragmento)
    except json.JSONDecodeError:
        reparado = _reparar_json(fragmento)
        return json.loads(reparado)


def _normalizar(data: dict) -> dict:
    apto = bool(data.get("apto"))
    try:
        puntaje = int(max(0, min(100, int(data.get("puntaje", 0)))))
    except (TypeError, ValueError):
        puntaje = 100 if apto else 0
    faltantes = data.get("faltantes") or []
    if not isinstance(faltantes, list):
        faltantes = []
    observaciones = data.get("observaciones") or []
    if isinstance(observaciones, str):
        observaciones = [observaciones]
    return {
        "apto": apto,
        "puntaje": puntaje,
        "faltantes": faltantes,
        "observaciones": observaciones,
        "resumen": str(data.get("resumen", "")).strip() or ("Se encontraron campos faltantes." if not apto else "Documento sin faltantes apreciables."),
    }


def dictamen_no_disponible(motivo: str) -> dict:
    return {
        "apto": None,
        "puntaje": None,
        "faltantes": [],
        "observaciones": [motivo],
        "resumen": "La revisión automática con IA no estuvo disponible para este documento.",
    }


async def validar_documento(tipo: str, nombre_archivo: str, contenido: bytes) -> dict:
    """Valida el documento. Siempre devuelve un dictamen (nunca lanza), para
    no romper el flujo de subida si la IA falla."""
    try:
        texto, truncado = extraer_texto(nombre_archivo, contenido)
    except SinTextoError as exc:
        return dictamen_no_disponible(str(exc))
    except Exception:  # pragma: no cover - defensivo
        logger.exception("Error extrayendo texto de %s", nombre_archivo)
        return dictamen_no_disponible("No se pudo leer el contenido del archivo.")

    if not settings.NVIDIA_API_KEY:
        return dictamen_no_disponible("El servicio de validación IA no está configurado en el servidor.")

    checklist = checklist_para(tipo)
    campos = "\n".join(f"{i + 1}. {campo}" for i, campo in enumerate(checklist["campos"]))
    prompt = (
        f"Valida el siguiente documento.\n"
        f"Formato: {checklist['nombre']}\n"
        f"Autoridad: {checklist['autoridad']}\n"
        f"Lista de verificación de campos que DEBEN venir diligenciados:\n{campos}\n\n"
        f"Texto del documento (nombre: {nombre_archivo}):\n<<<{texto}>>>\n"
        "Devuelve SOLO el JSON indicado."
    )
    if truncado:
        prompt += "\nNota: el texto fue truncado por tamaño; menciona en observaciones si faltan secciones visibles."

    try:
        # Hasta 2 intentos: a veces el modelo responde con JSON mal formado.
        for intento in range(2):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                    response = await client.post(
                        settings.NVIDIA_API_URL,
                        headers={
                            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": settings.NVIDIA_MODEL,
                            "messages": [
                                {"role": "system", "content": SYSTEM},
                                {"role": "user", "content": prompt},
                            ],
                            "temperature": 0.1,
                            "max_tokens": 900,
                        },
                    )
                    response.raise_for_status()
                    contento = response.json()["choices"][0]["message"]["content"]
                    return _normalizar(_parse_json(contento))
            except (ValueError, json.JSONDecodeError) as exc:
                if intento == 0:
                    logger.info("JSON de IA inválido en intento %d, reintentando…: %s", intento + 1, exc)
                    continue
                raise
        raise ValueError("No se obtuvo una respuesta válida tras los reintentos")
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        logger.warning("Validación IA no disponible para solicitud %s: %s", nombre_archivo, exc)
        return dictamen_no_disponible("El servicio de IA no respondió; el documento pasará a revisión manual.")
    except Exception:  # pragma: no cover
        logger.exception("Error inesperado validando %s", nombre_archivo)
        return dictamen_no_disponible("Error interno durante la validación automática.")


def ensamblar_dictamen(tipo: str, dictamen: dict, texto_truncado: bool = False) -> dict:
    return {
        "validacion_ia": {
            **dictamen,
            "tipo": tipo,
            "modelo": settings.NVIDIA_MODEL,
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "texto_truncado": texto_truncado,
        }
    }
