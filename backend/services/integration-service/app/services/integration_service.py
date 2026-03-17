import uuid
from app.api.schemas import IntegrationCreate, IntegrationUpdate
from app.models.integration import Integration
from app.repositories.integration_repo import IntegrationRepo


class IntegrationService:
    def __init__(self, repo: IntegrationRepo):
        self.repo = repo

    async def create(self, user_id: int, data: IntegrationCreate) -> Integration:
        return await self.repo.create(
            user_id=user_id,
            platform=data.platform.value,
            name=data.name,
            platform_config=data.platform_config,
        )

    async def get_by_id(self, integration_id: uuid.UUID, user_id: int) -> Integration:
        integration = await self.repo.get_by_id(integration_id)
        if not integration or integration.user_id != user_id:
            raise ValueError("Integration not found")
        return integration

    async def get_all(self, user_id: int) -> list[Integration]:
        return await self.repo.get_by_user(user_id)
    
    async def get_all_active(self)-> list[Integration]:
        return await self.repo.get_all_active()
    
    async def update(
        self,
        integration_id: uuid.UUID,
        user_id: int,
        data: IntegrationUpdate,
    ) -> Integration | None:
        integration = await self.get_by_id(integration_id, user_id)
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return integration
        return await self.repo.update(integration_id, **update_data)

    async def delete(self, integration_id: uuid.UUID, user_id: int) -> None:
        integration = await self.get_by_id(integration_id, user_id)
        await self.repo.delete(integration.id)
