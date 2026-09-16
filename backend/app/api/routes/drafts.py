import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.drafts import DraftRecord, draft_store
from app.database import get_db
from app.models.draft import Draft
from app.schemas.drafts import DraftRequest, DraftResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/formulario", tags=["Borradores"])


def _response(draft_id: str, version: int, data: dict, updated_at: datetime) -> DraftResponse:
    return DraftResponse(
        draft_id=draft_id,
        version=version,
        data=data,
        updated_at=updated_at,
    )


def _conflict_detail(draft_id: str, version: int, data: dict, updated_at: datetime):
    return {
        "message": "El borrador cambió en otra sesión.",
        "draft": _response(draft_id, version, data, updated_at).model_dump(mode="json"),
    }


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str, db: Session = Depends(get_db)) -> DraftResponse:
    try:
        row = db.get(Draft, draft_id)
        if row is not None:
            return _response(draft_id, row.version, row.data, row.updated_at)
    except SQLAlchemyError:
        logger.warning("DB no disponible para GET draft %s, fallback a memoria", draft_id)
        db.rollback()
    # Fallback memoria (tests sin DB / degradación graceful)
    record = draft_store.get(draft_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    return _response(draft_id, record.version, record.data, record.updated_at)


@router.put("/drafts/{draft_id}", response_model=DraftResponse)
async def put_draft(draft_id: str, payload: DraftRequest, db: Session = Depends(get_db)) -> DraftResponse:
    try:
        row = db.get(Draft, draft_id)
        current_version = row.version if row else 0
        if payload.version != current_version:
            if row is None:
                raise HTTPException(status_code=409, detail="El borrador cambió en otra sesión.")
            raise HTTPException(
                status_code=409,
                detail=_conflict_detail(draft_id, row.version, row.data, row.updated_at),
            )
        now = datetime.now(timezone.utc)
        if row is None:
            row = Draft(draft_id=draft_id, version=1, data=payload.data, updated_at=now)
            db.add(row)
        else:
            row.version = current_version + 1
            row.data = payload.data
            row.updated_at = now
        db.commit()
        db.refresh(row)
        # espejo en memoria para coherencia con fallback
        draft_store._records[draft_id] = DraftRecord(
            version=row.version, data=row.data, updated_at=row.updated_at
        )
        return _response(draft_id, row.version, row.data, row.updated_at)
    except HTTPException:
        raise
    except SQLAlchemyError:
        logger.warning("DB no disponible para PUT draft %s, fallback a memoria", draft_id)
        db.rollback()
        try:
            record = draft_store.put(draft_id, payload.version, payload.data)
        except ValueError as conflict:
            current = conflict.args[0]
            detail = "El borrador cambió en otra sesión."
            if current is not None:
                detail = {
                    "message": detail,
                    "draft": _response(draft_id, current.version, current.data, current.updated_at).model_dump(mode="json"),
                }
            raise HTTPException(status_code=409, detail=detail)
        return _response(draft_id, record.version, record.data, record.updated_at)
