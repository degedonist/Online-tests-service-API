from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.answer import AnswerCreate, AnswerUpdate, AnswerOut
from app.services.test_service import (
    get_question_by_id, get_test_by_id,
    create_answer, get_answer_by_id,
    get_answers_for_question, update_answer, delete_answer,
)

router = APIRouter(tags=["Answers"])


@router.get(
    "/questions/{question_id}/answers",
    response_model=List[AnswerOut],
    summary="Список ответов на вопрос",
    description=(
        "Возвращает все варианты ответов для указанного вопроса. "
        "Если тест скрыт и вы не владелец — 404."
    ),
    responses={
        200: {"description": "Список ответов"},
        404: {"description": "Вопрос не найден"},
    },
)
async def list_answers(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = await get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    test = await get_test_by_id(db, question.test_id)
    if test.is_hidden and test.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Тест не найден")

    return await get_answers_for_question(db, question_id)


@router.post(
    "/questions/{question_id}/answers",
    response_model=AnswerOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вариант ответа (только для владельца теста)",
    description=(
        "Добавляет ответ к вопросу. Поле `is_correct` указывает, правильный это ответ или нет. "
        "У одного вопроса может быть несколько правильных ответов. "
        "Добавлять может только владелец теста."
    ),
    responses={
        201: {"description": "Ответ создан"},
        403: {"description": "Только владелец теста может добавлять ответы"},
        404: {"description": "Вопрос не найден"},
    },
)
async def create(
    question_id: int,
    data: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = await get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    test = await get_test_by_id(db, question.test_id)
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец теста может добавлять ответы")

    return await create_answer(db, question_id, data.text, data.is_correct)


@router.put(
    "/answers/{answer_id}",
    response_model=AnswerOut,
    summary="Изменить ответ (только для владельца теста)",
    description=(
        "Меняет текст ответа и/или отметку `is_correct`. "
        "Редактировать может только владелец теста."
    ),
    responses={
        200: {"description": "Ответ обновлён"},
        403: {"description": "Только владелец теста может редактировать ответы"},
        404: {"description": "Ответ не найден"},
    },
)
async def update(
    answer_id: int,
    data: AnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = await get_answer_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Ответ не найден")

    question = await get_question_by_id(db, answer.question_id)
    test = await get_test_by_id(db, question.test_id)
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец теста может редактировать ответы")

    return await update_answer(db, answer_id, data.model_dump(exclude_unset=True))


@router.delete(
    "/answers/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ответ (только для владельца теста)",
    description=(
        "Удаляет один вариант ответа. "
        "Удалять может только владелец теста."
    ),
    responses={
        204: {"description": "Ответ удалён"},
        403: {"description": "Только владелец теста может удалять ответы"},
        404: {"description": "Ответ не найден"},
    },
)
async def delete(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = await get_answer_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Ответ не найден")

    question = await get_question_by_id(db, answer.question_id)
    test = await get_test_by_id(db, question.test_id)
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец теста может удалять ответы")

    await delete_answer(db, answer_id)
