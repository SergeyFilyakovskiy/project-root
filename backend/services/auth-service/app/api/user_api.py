from app.core.dependencies import postgres_dependency
from app.repositories.user_repo import UserDAO

from fastapi import APIRouter
from starlette import status


router = APIRouter(
    prefix='/user',
    tags=['user']
)

