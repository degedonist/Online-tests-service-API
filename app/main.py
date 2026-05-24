import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, tests, questions, user_answers

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("📄 Swagger docs: http://localhost:8000/docs")
    yield


app = FastAPI(
    title="Quiz API",
    description="API для создания и прохождения тестов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(tests.router)
app.include_router(questions.router)
app.include_router(user_answers.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
