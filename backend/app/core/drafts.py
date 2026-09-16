"""Fallback en memoria para drafts (tests sin DB / degradación graceful).

El almacenamiento primario es la tabla `drafts` en Postgres
(ver `app/models/draft.py` + migración `0003_create_drafts`).
Este store solo se usa cuando la DB no está disponible.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class DraftRecord:
    version: int
    data: dict[str, Any]
    updated_at: datetime


class InMemoryDraftStore:
    def __init__(self) -> None:
        self._records: dict[str, DraftRecord] = {}
        self._lock = Lock()

    def get(self, draft_id: str) -> DraftRecord | None:
        with self._lock:
            return self._records.get(draft_id)

    def put(
        self, draft_id: str, expected_version: int, data: dict[str, Any]
    ) -> DraftRecord:
        with self._lock:
            current = self._records.get(draft_id)
            current_version = current.version if current else 0
            if expected_version != current_version:
                raise ValueError(current)
            record = DraftRecord(
                version=current_version + 1,
                data=data,
                updated_at=datetime.now(timezone.utc),
            )
            self._records[draft_id] = record
            return record


draft_store = InMemoryDraftStore()
