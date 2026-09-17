"""Previsualización de documentos (DOCX / XLSX / PDF) con Gotenberg.

Recibe un archivo, lo convierte a PDF vía LibreOffice (Gotenberg) cuando es
necesario y lo devuelve como StreamingResponse. Esto permite al frontend
renderizar un solo formato (PDF) con react-pdf / vue-pdf-embed y conservar
toda la fidelidad visual original (logos, marcas de agua, estilos de celda…).

Endpoint:  POST /api/documents/preview
"""
import os

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["documents"])

GOTENBERG_URL = os.getenv("GOTENBERG_URL", "http://gotenberg:3000").rstrip("/")
CONVERT_ENDPOINT = f"{GOTENBERG_URL}/forms/libreoffice/convert"

# Extensiones admitidas por el endpoint
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
_MIME_MAP = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@router.post("/documents/preview")
async def preview_document(file: UploadFile = File(...)) -> StreamingResponse:
    """Recibe DOCX / XLSX / PDF y devuelve el PDF resultante como stream.

    - Si el archivo ya es PDF, se devuelve directamente (no pasa por Gotenberg).
    - Si es DOCX/XLSX se envía a Gotenberg (LibreOffice) para conversión.
    """
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    name = file.filename or "documento"
    ext = os.path.splitext(name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Formato no soportado: {ext or '(sin extensión)'}. "
                "Se admiten: .pdf, .docx, .xlsx"
            ),
        )

    # ── PDF directo ──────────────────────────────────────────────────────────
    if ext == ".pdf":
        return StreamingResponse(
            iter([raw]),
            media_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="preview.pdf"'},
        )

    # ── DOCX / XLSX → Gotenberg (LibreOffice) ────────────────────────────────
    mime = _MIME_MAP.get(ext)
    multipart = {"files": (name, raw, mime)}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(CONVERT_ENDPOINT, files=multipart)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="El servicio de conversión (Gotenberg) no está disponible. "
            "En local levanta el contenedor 'gotenberg' (docker compose); en "
            "producción define GOTENBERG_URL apuntando a una instancia externa.",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Gotenberg excedió el tiempo de espera al convertir el documento.",
        )

    if resp.status_code != 200:
        detail = resp.text or "Error desconocido en Gotenberg"
        raise HTTPException(
            status_code=502,
            detail=f"Error de Gotenberg al convertir: {detail[:400]}",
        )

    pdf_bytes = resp.content
    if not pdf_bytes:
        raise HTTPException(
            status_code=502,
            detail="Gotenberg devolvió una respuesta vacía.",
        )

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="preview.pdf"'},
    )