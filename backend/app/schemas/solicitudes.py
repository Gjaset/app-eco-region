from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SolicitudRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    usuario_email: str = ""
    usuario_nombre: str = ""
    tipo: str
    estado: str = "pendiente"
    nombre_archivo: str
    tamano_bytes: int
    creado_en: datetime
    resumen: dict[str, Any] | None = None
