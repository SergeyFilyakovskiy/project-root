from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from starlette import status

from app.api.schemas import RoleEnum
from app.core.dependencies import CurrentUser


class RoleChecker:
    """
    Класс для проверки роли пользователя.

    Используется как dependency в роутерах.

    Пример использования:
    - @router.get("/admin", dependencies=[Depends(admin_only)])
    - @router.get("/admin", dependencies=[Depends(manager_or_admin)])

    """

    def __init__(self, allowed_roles: Sequence[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user = CurrentUser):
        """
        Проверяет роль текущего пользователя.

        Аргументы:
        - current_user - данные пользователя из JWT токена

        Возвращает:
        - current_user если роль разрешена

        Исключения:
        - HTTPException 403 если роль не разрешена

        """
        if current_user.role not in self.allowed_roles: # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return current_user


