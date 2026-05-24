from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test import Test
from app.models.question import Question
from app.models.answer import Answer


async def create_test(db: AsyncSession, title: str, description: Optional[str], owner_id: int) -> Test:
    test = Test(title=title, description=description, owner_id=owner_id)
    db.add(test)
    await db.commit()
    await db.refresh(test)
    return test


async def get_test_by_id(db: AsyncSession, test_id: int) -> Optional[Test]:
    result = await db.execute(select(Test).where(Test.id == test_id))
    return result.scalar_one_or_none()


async def get_visible_tests(db: AsyncSession, current_user_id: int) -> List[Test]:
    result = await db.execute(
        select(Test).where(
            (Test.is_hidden == False) | (Test.owner_id == current_user_id)
        ).order_by(Test.id)
    )
    return result.scalars().all()


async def update_test(db: AsyncSession, test_id: int, data: dict) -> Optional[Test]:
    test = await get_test_by_id(db, test_id)
    if not test:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(test, key, value)
    await db.commit()
    await db.refresh(test)
    return test


async def delete_test(db: AsyncSession, test_id: int) -> bool:
    test = await get_test_by_id(db, test_id)
    if not test:
        return False
    await db.delete(test)
    await db.commit()
    return True


async def toggle_test_visibility(db: AsyncSession, test_id: int) -> Optional[Test]:
    test = await get_test_by_id(db, test_id)
    if not test:
        return None
    test.is_hidden = not test.is_hidden
    await db.commit()
    await db.refresh(test)
    return test


async def create_question(db: AsyncSession, test_id: int, text: str) -> Question:
    question = Question(text=text, test_id=test_id)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def get_question_by_id(db: AsyncSession, question_id: int) -> Optional[Question]:
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def update_question(db: AsyncSession, question_id: int, text: str) -> Optional[Question]:
    question = await get_question_by_id(db, question_id)
    if not question:
        return None
    question.text = text
    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    question = await get_question_by_id(db, question_id)
    if not question:
        return False
    await db.delete(question)
    await db.commit()
    return True


async def get_questions_for_test(db: AsyncSession, test_id: int) -> List[Question]:
    result = await db.execute(
        select(Question).where(Question.test_id == test_id).order_by(Question.id)
    )
    return result.scalars().all()


async def create_answer(db: AsyncSession, question_id: int, text: str, is_correct: bool) -> Answer:
    answer = Answer(text=text, is_correct=is_correct, question_id=question_id)
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def get_answer_by_id(db: AsyncSession, answer_id: int) -> Optional[Answer]:
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    return result.scalar_one_or_none()


async def update_answer(db: AsyncSession, answer_id: int, data: dict) -> Optional[Answer]:
    answer = await get_answer_by_id(db, answer_id)
    if not answer:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(answer, key, value)
    await db.commit()
    await db.refresh(answer)
    return answer


async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    answer = await get_answer_by_id(db, answer_id)
    if not answer:
        return False
    await db.delete(answer)
    await db.commit()
    return True


async def get_answers_for_question(db: AsyncSession, question_id: int) -> List[Answer]:
    result = await db.execute(
        select(Answer).where(Answer.question_id == question_id).order_by(Answer.id)
    )
    return result.scalars().all()
