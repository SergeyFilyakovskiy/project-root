from fastapi import APIRouter
from starlette import status

from app.api.schemas import UserRegisterSchema
from app.core.dependencies import postgres_dependency
from app.repositories.user_repo import UserDAO

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', status_code= status.HTTP_201_CREATED)
async def create_new_user(
    request: UserRegisterSchema,
    db: postgres_dependency,
)-> None:
    
    await UserDAO.add_user_with_profile(
        session=db,
        user_data=request
    )
    