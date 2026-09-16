import logging

import httpx
from fastapi import APIRouter

from app.config import settings
from app.core.ia.conocimiento import ficha_para
from app.core.ia.guardarrailes import RECHAZO_AMABLE, necesita_rechazo
from app.schemas.ia import AgenteRequest, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ia", tags=["IA"])
FALLBACK_REPLY = (
    "Puedo ayudarte a completar el trámite. Revisa los datos del titular, "
    "la ubicación, el tipo de aprovechamiento y los soportes de la autoridad "
    "seleccionada."
)
AGENTE_FALLBACK = (
    "Puedo orientarte sobre permisos y requisitos ante la CAR, la SDA o "
    "Corpoboyacá: anexos exigidos, pasos para radicar y datos del formulario. "
    "¿Sobre cuál entidad es tu consulta?"
)
SYSTEM_AGENTE = """Eres el agente oficial de EcoRegión para permisos forestales ante la CAR \
Cundinamarca, la Secretaría Distrital de Ambiente (SDA) y Corpoboyacá.
REGLAS INQUEBRANTABLES:
1. Responde ÚNICAMENTE sobre procedimientos, requisitos y documentos para permisos de \
aprovechamiento forestal ante esas tres entidades.
2. Si la pregunta es de otro tema, responde EXACTAMENTE: «RECHAZO».
3. Responde en español colombiano, claro y accionable: pasos o lista de documentos.
4. Usa la FICHA DE LA ENTIDAD del contexto; si el dato no está ahí, dilo y remite a la \
entidad. No inventes resoluciones, costos ni plazos.
5. Máximo 900 caracteres.""".replace("«RECHAZO»", f"«{RECHAZO_AMABLE}»")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    if not settings.NVIDIA_API_KEY:
        return ChatResponse(reply=FALLBACK_REPLY, fallback=True)

    request_body = {
        "model": settings.NVIDIA_MODEL,
        "messages": [message.model_dump() for message in payload.messages],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            response = await client.post(
                settings.NVIDIA_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Nvidia returned an empty response")
            return ChatResponse(reply=content.strip(), model=settings.NVIDIA_MODEL)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        logger.exception("Nvidia chat request failed")
        return ChatResponse(
            reply=FALLBACK_REPLY,
            fallback=True,
            model=settings.NVIDIA_MODEL,
        )


@router.post("/agente", response_model=ChatResponse)
async def agente(payload: AgenteRequest) -> ChatResponse:
    """Agente con candado temático: solo CAR, SDA y Corpoboyacá.

    El filtro de alcance se aplica sin llamar a NIM cuando la pregunta
    llega sin historial y no menciona el tema; con historial (repreguntas
    como «¿y cuánto cuesta?») decide el modelo con el system prompt.
    """
    pregunta = payload.pregunta.strip()
    if not payload.historial and necesita_rechazo(pregunta):
        return ChatResponse(reply=RECHAZO_AMABLE)
    if not settings.NVIDIA_API_KEY:
        return ChatResponse(reply=AGENTE_FALLBACK, fallback=True)

    messages = [
        {"role": "system", "content": f"{SYSTEM_AGENTE}\n\n{ficha_para(pregunta)}"},
        *(m.model_dump() for m in payload.historial[-6:]),
        {"role": "user", "content": pregunta},
    ]
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25.0)) as client:
            response = await client.post(
                settings.NVIDIA_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.NVIDIA_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "max_tokens": 400,
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Nvidia returned an empty response")
            return ChatResponse(reply=content.strip()[:2000], model=settings.NVIDIA_MODEL)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        logger.exception("Nvidia agente request failed")
        return ChatResponse(
            reply=AGENTE_FALLBACK,
            fallback=True,
            model=settings.NVIDIA_MODEL,
        )
