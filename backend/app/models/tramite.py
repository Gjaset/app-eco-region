import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class EstadoTramite(str, enum.Enum):
    BORRADOR = "borrador"
    EN_REVISION = "en_revision"
    LISTO_RADICAR = "listo_radicar"
    RADICADO = "radicado"
    APROBADO = "aprobado"
    DEVUELTO = "devuelto"

class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    nit: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    representante_legal: Mapped[str | None] = mapped_column(String)
    direccion: Mapped[str | None] = mapped_column(String)
    creado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tramites: Mapped[list["Tramite"]] = relationship(back_populates="cliente")

class Tramite(Base):
    __tablename__ = "tramites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"))
    tipo_tramite: Mapped[str | None] = mapped_column(String, default="aprovechamiento_forestal")
    estado: Mapped[EstadoTramite | None] = mapped_column(Enum(EstadoTramite), default=EstadoTramite.BORRADOR)
    datos_formulario: Mapped[dict | None] = mapped_column(JSON)
    datos_normalizados: Mapped[dict | None] = mapped_column(JSON)
    autoridad_sigla: Mapped[str | None] = mapped_column(String)
    municipio_dane: Mapped[str | None] = mapped_column(String)
    creado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    radicado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    numero_radicado: Mapped[str | None] = mapped_column(String)
    cliente: Mapped[Cliente | None] = relationship(back_populates="tramites")
    documentos: Mapped[list["Documento"]] = relationship(back_populates="tramite")

class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tramite_id: Mapped[int | None] = mapped_column(ForeignKey("tramites.id"))
    tipo: Mapped[str | None] = mapped_column(String)
    nombre: Mapped[str | None] = mapped_column(String)
    ruta: Mapped[str | None] = mapped_column(String)
    generado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tramite: Mapped[Tramite | None] = relationship(back_populates="documentos")