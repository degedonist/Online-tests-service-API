from typing import Optional
from pydantic import BaseModel


class QuestionCreate(BaseModel):
    text: str


class QuestionUpdate(BaseModel):
    text: Optional[str] = None


class QuestionOut(BaseModel):
    id: int
    text: str
    test_id: int

    model_config = {"from_attributes": True}
