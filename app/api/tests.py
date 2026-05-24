from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.test import TestCreate, TestUpdate, TestOut
from app.services.test_service import (
    create_test, get_test_by_id, get_visible_tests,
    update_test, delete_test, toggle_test_visibility,
)

router = APIRouter(prefix="/tests", tags=["Tests"])


@router.get(
    "/",
    response_model=List[TestOut],
    summary="Список всех тестов, которые видны пользователю",
    description=(
        "Показывает все тесты, которые не скрыты. Если тест скрыт — его увидит только владелец. "
        "Для вызова нужно передать JWT-токен в заголовке `Authorization: Bearer <токен>`."
    ),
    responses={
        200: {"description": "Список тестов"},
        401: {"description": "Не передан или невалидный токен"},
    },
)
async def list_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_visible_tests(db, current_user.id)


@router.post(
    "/",
    response_model=TestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый тест",
    description=(
        "Создаёт тест с названием и описанием. Владельцем теста автоматически становится текущий пользователь. "
        "Для вызова нужно передать JWT-токен."
    ),
    responses={
        201: {"description": "Тест успешно создан"},
        401: {"description": "Не передан или невалидный токен"},
    },
)
async def create(
    data: TestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_test(db, data.title, data.description, current_user.id)


@router.get(
    "/{test_id}",
    response_model=TestOut,
    summary="Получить конкретный тест по ID",
    description=(
        "Возвращает данные теста: название, описание, видимость, даты создания и обновления. "
        "Если тест скрыт и вы не его владелец — вернётся 404 (тест не найден)."
    ),
    responses={
        200: {"description": "Данные теста"},
        404: {"description": "Тест не найден"},
    },
)
async def get_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.is_hidden and test.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Тест не найден")
    return test


@router.put(
    "/{test_id}",
    response_model=TestOut,
    summary="Изменить тест (только для владельца)",
    description=(
        "Обновляет название и/или описание теста. "
        "Менять тест может только тот, кто его создал. "
        "Если теста нет — 404, если вы не владелец — 403."
    ),
    responses={
        200: {"description": "Тест обновлён"},
        403: {"description": "Только владелец может редактировать тест"},
        404: {"description": "Тест не найден"},
    },
)
async def update(
    test_id: int,
    data: TestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может редактировать тест")

    return await update_test(db, test_id, data.model_dump(exclude_unset=True))


@router.delete(
    "/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тест (только для владельца)",
    description=(
        "Полностью удаляет тест вместе со всеми вопросами и ответами. "
        "Удалять может только создатель теста."
    ),
    responses={
        204: {"description": "Тест удалён (тело ответа пустое)"},
        403: {"description": "Только владелец может удалить тест"},
        404: {"description": "Тест не найден"},
    },
)
async def delete(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может удалить тест")

    await delete_test(db, test_id)


@router.patch(
    "/{test_id}/visibility",
    response_model=TestOut,
    summary="Скрыть или раскрыть тест (только для владельца)",
    description=(
        "Переключает видимость теста: если был скрыт — становится видимым, если был видим — скрывается. "
        "Скрытые тесты видны в общем списке только владельцу. "
        "Управлять видимостью может только создатель теста."
    ),
    responses={
        200: {"description": "Видимость изменена (поле is_hidden обновлено)"},
        403: {"description": "Только владелец может скрыть/раскрыть тест"},
        404: {"description": "Тест не найден"},
    },
)
async def visibility(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = await get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Тест не найден")
    if test.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может скрыть/раскрыть тест")

    return await toggle_test_visibility(db, test_id)
