from app.core.dependencies import postgres_dependency, CurrentUser
from app.models.user import Profile
from app.repositories.user_repo import ProfileDAO
from app.api.schemas import ProfileResponseSchema, ProfileUpdateSchema

from fastapi import APIRouter, HTTPException
from starlette import status


router = APIRouter(
    prefix='/profile',
    tags=['profile']
)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_profile_info(
    db: postgres_dependency,
    current_user: CurrentUser
) -> ProfileResponseSchema:
    """
    Получить профиль текущего авторизованного пользователя.

    Args:
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Raises:
        HTTPException: 404 если профиль не найден.

    Returns:
        ProfileResponseSchema: Данные профиля пользователя.
    """
    profile = await ProfileDAO.find_by_user_id(
        session=db,
        user_id=current_user.id,
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found'
        )
    return ProfileResponseSchema.model_validate(profile)


@router.patch("/me", status_code=status.HTTP_200_OK)
async def update_profile_info(
    request: ProfileUpdateSchema,
    db: postgres_dependency,
    current_user: CurrentUser
) -> ProfileResponseSchema:
    """
    Обновить профиль текущего авторизованного пользователя.

    Args:
        request: Данные для обновления (все поля опциональны).
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Raises:
        HTTPException: 404 если профиль не найден.

    Returns:
        ProfileResponseSchema: Обновлённые данные профиля.
    """
    profile = await ProfileDAO.find_by_user_id(session=db, user_id=current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found'
        )
    updated_profile = await ProfileDAO.update_by_id(
        session=db,
        id=current_user.id,
        data=request.model_dump(exclude_none=True)
    )
    return ProfileResponseSchema.model_validate(updated_profile)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_profile_by_user_id(
    user_id: int,
    db: postgres_dependency,
    current_user: CurrentUser
) -> ProfileResponseSchema:
    """
    Получить профиль пользователя по user_id.

    Args:
        user_id: Идентификатор пользователя.
        db: Сессия базы данных.
        current_user: Текущий авторизованный пользователь из токена.

    Raises:
        HTTPException: 404 если профиль не найден.

    Returns:
        ProfileResponseSchema: Данные профиля пользователя.
    """
    profile = await ProfileDAO.find_by_user_id(session=db, user_id=user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found'
        )
    return ProfileResponseSchema.model_validate(profile)