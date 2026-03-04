

from typing import Sequence

from fastapi import Depends, HTTPException

from app.api.schemas import TokenData

from starlette import status

class RoleChecker:

    """

    Класс для проверки роли пользователя
    
    """

    def __init__(self, allowed_roles: Sequence[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: TokenData = Depends(get_current_user)):
            

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operation not permitted"
            )
        
        return current_user
    
admin_only = RoleChecker(["admin", "super_admin"])