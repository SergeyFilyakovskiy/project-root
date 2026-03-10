from app.core.dependencies import postgres_dependency, CurrentUser
from app.models.user import Profile
from app.repositories.user_repo import ProfileDAO
from app.api.schemas import ProfileResponseSchema

from fastapi import APIRouter
from starlette import status


router = APIRouter(
    prefix='/profile',
    tags=['profile']
)

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_profile_info(
    db: postgres_dependency,
    current_user: CurrentUser
)-> ProfileResponseSchema | None:
    
    profile_info = await ProfileDAO.find_by_user_id(
            session=db,
            user_id= current_user.id,
            )
    return ProfileResponseSchema.model_validate(profile_info)
    
    
