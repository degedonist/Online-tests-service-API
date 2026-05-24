from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_answer import UserAnswerSubmit, UserAnswerOut, ResultItem
from app.services.user_answer_service import (
    submit_answer, get_user_results_for_test, get_all_results_for_test,
)
from app.services.test_service import get_test_by_id

router = APIRouter(tags=["User Answers"])


@router.post(
    "/tests/{test_id}/pass",
    response_model=UserAnswerOut,
    status_code=status.HTTP_201_CREATED,
    summary="Ответить на вопрос теста",
    description=(
        "Отправляет ответ пользователя на конкретный вопрос в тесте. "
        "Нужно передать ID вопроса и ID выбранного ответа. "
        "Можно отвечать на один и тот же вопрос несколько раз — каждый ответ сохраняется. "
        "Тест должен существовать и не быть скрытым (если вы не владелец)."
    ),
    responses={
        201: {"description": "Ответ записан"},
        400: {"description": "Некорректный вопрос или ответ (например, ответ не принадлежит этому вопросу)"},
        404: {"description": "Тест не найден"},
    },
)
async def pass_test(
    test_id: int,
    data: UserAnswerSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.is_hidden and test.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Тест не найден")

    ua = await submit_answer(db, current_user.id, data.question_id, data.answer_id)
    if not ua:
        raise HTTPException(status_code=400, detail="Некорректный вопрос или ответ")
    return ua


@router.get(
    "/tests/{test_id}/results",
    response_model=List[ResultItem],
    summary="Посмотреть результаты прохождения теста",
    description=(
        "Показывает все ответы пользователя на вопросы теста: "
        "текст вопроса, выбранный ответ, правильный он или нет, и дата ответа. "
        "Если запрашивает владелец теста — показываются ответы ВСЕХ пользователей. "
        "Если запрашивает обычный пользователь — только его собственные ответы."
    ),
    responses={
        200: {"description": "Список ответов с результатами"},
        404: {"description": "Тест не найден"},
    },
)
async def get_results(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")

    if test.owner_id == current_user.id:
        return await get_all_results_for_test(db, test_id)
    return await get_user_results_for_test(db, current_user.id, test_id)
