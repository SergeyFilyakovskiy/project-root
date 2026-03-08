from typing import Annotated

from fastapi import Cookie, HTTPException, Depends
from starlette import status

from app.api.schemas import TokenData
from app.core.security import Token

def get_current_user(
        token: None | str = Cookie(default= None, alias="access")
        )-> TokenData:
    
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
        )

    return Token.get_token_payload(token)

CurrentUser = Annotated[TokenData, Depends(get_current_user)]
