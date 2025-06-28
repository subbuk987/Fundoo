from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: Optional[str] = None
    labels: List[str]


class LabelRead(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class NoteRead(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    created_at: datetime
    labels: List[LabelRead]

    model_config = {"from_attributes": True}


class NoteSuccessResponse(BaseModel):
    message: str
    payload: NoteRead
    status_code: int
