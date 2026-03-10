from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette import status

from app.api.schemas import UserRegisterSchema, UserLoginSchema
from app.core.dependencies import postgres_dependency, CurrentUser, redis_dependency
from app.repositories.user_repo import UserDAO
from app.services.user_service import authenticate_user
from app.core.security import Token

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
    
@router.post('/login')
async def login(
    request: UserLoginSchema,
    postgres_session: postgres_dependency,
    redis_session: redis_dependency,
):
    user = await authenticate_user(request, postgres_session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    tokens = Token()
    tokens.encode_access_token(user)
    tokens.encode_refresh_token(user)
    await tokens.save_refresh_token_in_redis(
        user=user, 
        session= redis_session,
        )
    response = JSONResponse({"detail": "logged in"})
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value= tokens.refresh_token,
        httponly= True,
        path="/auth"
    )
    return response