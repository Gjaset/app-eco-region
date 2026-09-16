from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Solicitud(Base):
    """Copia de cada documento exportado por un usuario (trazabilidad para admin)."""

    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="fun")
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente")
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta_archivo: Mapped[str] = mapped_column(String(512), nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Contenido del documento en la DB: portable a serverless (Vercel no
    # tiene disco persistente). El archivo en GENERATED_PATH queda como
    # copia local opcional solo en desarrollo.
    contenido: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    resumen: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    usuario: Mapped["Usuario"] = relationship()
