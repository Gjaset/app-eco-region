from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)


class ChatResponse(BaseModel):
    reply: str
    fallback: bool = False
    model: str | None = None


class AgenteRequest(BaseModel):
    """Pregunta + historial reciente; el prompt sistema lo construye el servidor."""

    pregunta: str = Field(min_length=1, max_length=1000)
    historial: list[ChatMessage] = Field(default_factory=list, max_length=6)
