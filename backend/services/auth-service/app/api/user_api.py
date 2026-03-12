from app.api.schemas import UserChangePasswordSchema, UserResponseSchema, UserUpdateRoleSchema, UserUpdateSchema
from app.core.dependencies import CurrentUser, postgres_dependency
from app.core.security import hash_password, verify_password
from app.models.user import RoleEnum
from app.services.role_service import admin_only
from app.repositories.user_repo import UserDAO

from fastapi import APIRouter, HTTPException
from starlette import status


router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/me', status_code=status.HTTP_200_OK)
async def get_user_info(
    db: postgres_dependency,
    current_user: CurrentUser
) -> UserResponseSchema:
    
    """
    Получить данные текущего авторизованного пользователя.

    Args:
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Returns:
        UserResponseSchema: Данные пользователя (id, username, email).
    """

    user = await UserDAO.find_by_id(session=db, id=current_user.id)
    return UserResponseSchema.model_validate(user)


@router.patch('/me', status_code=status.HTTP_200_OK)
async def update_current_user(
    request: UserUpdateSchema,
    db: postgres_dependency,
    current_user: CurrentUser
) -> UserResponseSchema:
    
    """
    Обновить данные текущего авторизованного пользователя.

    Args:
        request: Данные для обновления (username, email, password — все опциональны).
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Returns:
        UserResponseSchema: Обновлённые данные пользователя.
    """

    updated_user = await UserDAO.update_by_id(
        session=db,
        id=current_user.id,
        data=request.model_dump()
    )
    return UserResponseSchema.model_validate(updated_user)


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: postgres_dependency,
    current_user: CurrentUser
) -> None:
    """
    Удалить аккаунт текущего авторизованного пользователя.

    Args:
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Returns:
        None
    """
    await UserDAO.delete_by_id(session=db, id=current_user.id)


@router.get('/{user_id}', status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int,
    db: postgres_dependency,
    current_user: CurrentUser,
    role: admin_only
) -> UserResponseSchema:
    """
    Получить данные пользователя по id. Доступно только администратору.

    Args:
        user_id: Идентификатор искомого пользователя.
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.
        role: Проверка роли администратора.

    Raises:
        HTTPException: 404 если пользователь с указанным id не найден.

    Returns:
        UserResponseSchema: Данные найденного пользователя.
    """
    user = await UserDAO.find_by_id(session=db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return UserResponseSchema.model_validate(user)

@router.patch('/me/password', status_code=status.HTTP_200_OK)
async def change_password(
    request: UserChangePasswordSchema,
    postgres_connection: postgres_dependency,
    current_user: CurrentUser
) -> None:
    """
    Сменить пароль текущего авторизованного пользователя.

    Args:
        request: Текущий и новый пароль пользователя.
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Raises:
        HTTPException: 400 если старый пароль введён неверно.

    Returns:
        None
    """
    user = await UserDAO.find_by_id(
        session=postgres_connection, 
        id=current_user.id
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found'
        )

    if not verify_password(request.old_password, user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Old password is incorrect'
        )

    await UserDAO.update_password(
        session=postgres_connection,
        user_id=current_user.id,
        hashed_password=hash_password(request.new_password)
    )


@router.patch('/{user_id}/role', status_code=status.HTTP_200_OK)
async def update_user_role(
    request: UserUpdateRoleSchema,
    postgres_connection: postgres_dependency,
    current_user: CurrentUser,
    role: admin_only
) -> UserResponseSchema:
    """
    Обновить роль пользователя. Доступно только администратору.

    Args:
        request: Идентификатор пользователя и новая роль.
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.
        role: Проверка роли администратора.

    Raises:
        HTTPException: 404 если пользователь с указанным id не найден.

    Returns:
        UserResponseSchema: Обновлённые данные пользователя.
    """

    user = await UserDAO.find_by_id(session=postgres_connection, id=request.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    updated_user = await UserDAO.update_role(
        session=postgres_connection,
        user_id=request.user_id,
        role= request.role
    )
    
    return UserResponseSchema.model_validate(updated_user)
