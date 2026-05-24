from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.models.answer import Answer
from app.schemas.user_answer import ResultItem


async def submit_answer(
    db: AsyncSession, user_id: int, question_id: int, answer_id: int
) -> Optional[UserAnswer]:
    question = await db.get(Question, question_id)
    if not question:
        return None

    answer = await db.get(Answer, answer_id)
    if not answer or answer.question_id != question_id:
        return None

    ua = UserAnswer(user_id=user_id, question_id=question_id, answer_id=answer_id)
    db.add(ua)
    await db.commit()
    await db.refresh(ua)
    return ua


async def get_user_results_for_test(
    db: AsyncSession, user_id: int, test_id: int
) -> List[ResultItem]:
    result = await db.execute(
        select(UserAnswer)
        .options(
            selectinload(UserAnswer.question),
            selectinload(UserAnswer.answer),
        )
        .where(UserAnswer.user_id == user_id)
        .order_by(UserAnswer.question_id)
    )
    rows = result.scalars().all()

    items = []
    for ua in rows:
        if ua.question.test_id != test_id:
            continue
        question = ua.question
        answer = ua.answer
        items.append(ResultItem(
            question_id=question.id,
            question_text=question.text,
            answer_id=answer.id,
            answer_text=answer.text,
            is_correct=answer.is_correct,
            submitted_at=ua.created_at,
        ))
    return items


async def get_all_results_for_test(
    db: AsyncSession, test_id: int
) -> List[ResultItem]:
    result = await db.execute(
        select(UserAnswer)
        .options(
            selectinload(UserAnswer.question),
            selectinload(UserAnswer.answer),
        )
        .order_by(UserAnswer.user_id, UserAnswer.question_id)
    )
    rows = result.scalars().all()

    items = []
    for ua in rows:
        if ua.question.test_id != test_id:
            continue
        question = ua.question
        answer = ua.answer
        items.append(ResultItem(
            question_id=question.id,
            question_text=question.text,
            answer_id=answer.id,
            answer_text=answer.text,
            is_correct=answer.is_correct,
            submitted_at=ua.created_at,
        ))
    return items
