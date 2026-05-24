from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.services.auth import hash_password, authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description=(
        "Создаёт нового пользователя по имени и паролю. "
        "Поле `confirm_password` должно совпадать с `password`, иначе вернётся ошибка 400. "
        "Если пользователь с таким именем уже существует — ошибка 409."
    ),
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Пароли не совпадают"},
        409: {"description": "Пользователь с таким именем уже существует"},
    },
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Пользователь уже существует")

    user = User(username=data.username, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Авторизация (вход в систему)",
    description=(
        "Проверяет имя пользователя и пароль. "
        "Если всё верно — возвращает JWT-токен, который нужно подставлять "
        "в заголовок `Authorization: Bearer <токен>` при вызовах остальных endpoint'ов."
    ),
    responses={
        200: {"description": "Успешный вход, токен получен"},
        401: {"description": "Неверное имя пользователя или пароль"},
    },
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")
