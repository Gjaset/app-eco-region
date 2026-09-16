from pydantic import BaseModel, Field
from typing import Any, Optional, List

class Titular(BaseModel):
    nombre: str
    nit: str
    representante_legal: str
    direccion: str

class Predio(BaseModel):
    nombre: str
    municipio: str
    vereda: Optional[str] = None
    latitud: str
    longitud: str

class Aprovechamiento(BaseModel):
    tipo: str
    justificacion: str
    volumen_total: float
    unidad: str

class Especie(BaseModel):
    nombre: str
    cantidad: int
    diametro_cm: Optional[float] = None

class FormularioCompleto(BaseModel):
    titular: Titular
    predio: Predio
    aprovechamiento: Aprovechamiento
    especies: List[Especie]
    autoridad_seleccionada: Optional[str] = None
    detalles_autoridad: dict[str, Any] = Field(default_factory=dict)
    confirmar_revision: bool = False