from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DraftRequest(BaseModel):
    version: int = Field(ge=0)
    data: dict[str, Any]


class DraftResponse(BaseModel):
    draft_id: str
    version: int
    data: dict[str, Any]
    updated_at: datetime
