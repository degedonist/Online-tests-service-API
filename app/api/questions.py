from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionOut
from app.services.test_service import (
    get_test_by_id, create_question, get_question_by_id,
    get_questions_for_test, update_question, delete_question,
)

router = APIRouter(tags=["Questions"])


@router.get(
    "/tests/{test_id}/questions",
    response_model=List[QuestionOut],
    summary="Список вопросов теста",
    description=(
        "Возвращает все вопросы, которые есть в указанном тесте. "
        "Если тест скрыт и вы не владелец — 404."
    ),
    responses={
        200: {"description": "Список вопросов"},
        404: {"description": "Тест не найден"},
    },
)
async def list_questions(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.is_hidden and test.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Тест не найден")
    return await get_questions_for_test(db, test_id)


@router.post(
    "/tests/{test_id}/questions",
    response_model=QuestionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вопрос в тест (только для владельца)",
    description=(
        "Создаёт новый вопрос в указанном тесте. "
        "Добавлять вопросы может только владелец теста."
    ),
    responses={
        201: {"description": "Вопрос создан"},
        403: {"description": "Только владелец может добавлять вопросы"},
        404: {"description": "Тест не найден"},
    },
)
async def create(
    test_id: int,
    data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может добавлять вопросы")

    return await create_question(db, test_id, data.text)


@router.put(
    "/questions/{question_id}",
    response_model=QuestionOut,
    summary="Изменить текст вопроса (только для владельца теста)",
    description=(
        "Обновляет текст вопроса. "
        "Редактировать может только владелец теста, которому принадлежит вопрос."
    ),
    responses={
        200: {"description": "Вопрос обновлён"},
        403: {"description": "Только владелец теста может редактировать вопросы"},
        404: {"description": "Вопрос не найден"},
    },
)
async def update(
    question_id: int,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = await get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    test = await get_test_by_id(db, question.test_id)
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец теста может редактировать вопросы")

    return await update_question(db, question_id, data.text)


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос (только для владельца теста)",
    description=(
        "Удаляет вопрос вместе со всеми ответами к нему. "
        "Удалять может только владелец теста."
    ),
    responses={
        204: {"description": "Вопрос удалён"},
        403: {"description": "Только владелец теста может удалять вопросы"},
        404: {"description": "Вопрос не найден"},
    },
)
async def delete(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = await get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    test = await get_test_by_id(db, question.test_id)
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец теста может удалять вопросы")

    await delete_question(db, question_id)
