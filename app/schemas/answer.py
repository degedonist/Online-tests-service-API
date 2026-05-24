from typing import Optional
from pydantic import BaseModel


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool = False


class AnswerUpdate(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class AnswerOut(BaseModel):
    id: int
    text: str
    is_correct: bool
    question_id: int

    model_config = {"from_attributes": True}
