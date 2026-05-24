from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TestOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_hidden: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
