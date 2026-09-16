from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tramite import EstadoTramite
from app.schemas.formulario import FormularioCompleto


class ClienteCreate(BaseModel):
    nombre: str = Field(min_length=1)
    nit: str = Field(min_length=3)
    representante_legal: str | None = None
    direccion: str | None = None


class ClienteRead(ClienteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creado_en: datetime | None = None


class TramiteCreate(BaseModel):
    cliente_id: int
    formulario: FormularioCompleto


class TramiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int | None
    tipo_tramite: str | None
    estado: EstadoTramite | None
    datos_formulario: dict | None
    datos_normalizados: dict | None
    autoridad_sigla: str | None
    municipio_dane: str | None
    creado_en: datetime | None
    actualizado_en: datetime | None
    radicado_en: datetime | None
    numero_radicado: str | None


class EstadoUpdate(BaseModel):
    estado: EstadoTramite
    numero_radicado: str | None = None
