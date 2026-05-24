from datetime import datetime
from pydantic import BaseModel


class UserAnswerSubmit(BaseModel):
    question_id: int
    answer_id: int


class UserAnswerOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    answer_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ResultItem(BaseModel):
    question_id: int
    question_text: str
    answer_id: int
    answer_text: str
    is_correct: bool
    submitted_at: datetime
