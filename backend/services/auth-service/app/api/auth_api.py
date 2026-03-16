from typing import Annotated

from fastapi import APIRouter, HTTPException, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from starlette import status

from app.api.schemas import UserRegisterSchema, TokenSchema
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
    """
    Зарегистрировать нового пользователя.

    Args:
        request: Данные для регистрации (username, email, password и данные профиля).
        db: Сессия базы данных.

    Returns:
        None
    """

    await UserDAO.add_user_with_profile(
        session=db,
        user_data=request
    )
    
@router.post('/login', status_code=status.HTTP_200_OK)
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    postgres_session: postgres_dependency,
    redis_session: redis_dependency,
):
    """
    Авторизовать пользователя и выдать access и refresh токены в куки.

    Args:
        request: Форма с username и password (OAuth2PasswordRequestForm).
        postgres_session: Сессия базы данных PostgreSQL.
        redis_session: Сессия Redis для хранения refresh токена.

    Raises:
        HTTPException: 404 если пользователь с указанными данными не найден.

    Returns:
        JSONResponse: Сообщение об успешном входе с токенами в куках.
    """
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
        path="/"
    )
    return response

@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(
    redis_connection: redis_dependency,
    current_user: CurrentUser,
    refresh_token: str = Cookie(alias='refresh_token')
):
    """
    Выйти из аккаунта: отозвать refresh токен и очистить куки.

    Args:
        redis_connection: Сессия Redis для проверки и отзыва токена.
        current_user: Текущий авторизованный пользователь из токена.
        refresh_token: Refresh токен из куки.

    Raises:
        HTTPException: 400 если refresh токен невалиден или уже отозван.

    Returns:
        JSONResponse: Сообщение об успешном выходе с очищенными куками.
    """
    token = TokenSchema(token= refresh_token, token_type='refresh')
    
    if not await Token.is_valid(token, redis_connection):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Your token is not valid'
        )
    
    await Token.revoke(token, redis_connection)
    
    
    response = JSONResponse({'detail':'logged out'})
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')

    return response


@router.post('/refresh', status_code=status.HTTP_200_OK)
async def refresh_access_token(
    redis_connection: redis_dependency,
    postgres_connection: postgres_dependency,
    refresh_token: str = Cookie(alias='refresh_token')
):
    """
    Обновить access токен по действующему refresh токену.

    Args:
        redis_connection: Сессия Redis для валидации refresh токена.
        postgres_connection: Сессия базы данных для получения данных пользователя.
        refresh_token: Refresh токен из куки.

    Raises:
        HTTPException: 401 если refresh токен невалиден или истёк.
        HTTPException: 404 если пользователь из токена не найден в базе.

    Returns:
        JSONResponse: Сообщение об успехе с новым access токеном в куке.
    """

    token_schema = TokenSchema(token= refresh_token, token_type='refresh')
    
    if not await Token.is_valid(token_schema, redis_connection):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your token is not valid'
        )
    
    user_data = Token.decode_token(token_schema.token)
    user = await UserDAO.find_by_id(session=postgres_connection, id=int(user_data['sub']))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    token = Token()
    token.encode_access_token(user)
    token.encode_refresh_token(user)

    await token.revoke(token_schema, redis_connection)
    await token.save_refresh_token_in_redis(user, redis_connection)
    response = JSONResponse({'detail': 'new access token created'})
    response.set_cookie(
        key='access_token',
        value=token.access_token,
        httponly=True,
        path='/'
    )
    response.set_cookie(
    key='refresh_token',
    value=token.refresh_token,
    httponly=True,
    path='/'
    )

    return response


@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_token(current_user: CurrentUser):
    """
    Верифицировать access токен и вернуть данные пользователя.
    Используется api-gateway для проверки каждого запроса.

    Args:
        current_user: Текущий авторизованный пользователь из токена.

    Returns:
        dict: id, email и role пользователя.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }
