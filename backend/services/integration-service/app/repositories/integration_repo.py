from datetime import datetime
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration import Integration

class IntegrationRepo:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
            self, 
            user_id: int, 
            platform: str, 
            name: str, 
            platform_config: dict
    )-> Integration:
        
        integration = Integration(
            user_id = user_id,
            platform = platform,
            name = name,
            platform_config = platform_config,
        )

        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)

        return integration
    
    async def get_by_id(
            self, 
            integration_id: uuid.UUID
    ) -> Integration | None:
        
        result = await self.session.execute(
            select(Integration).where(Integration.id == integration_id)
        )

        return result.scalar_one_or_none()
    
    async def get_by_user(
            self,
            user_id: int,
    )-> list[Integration]:
        
        result = await self.session.execute(
            select(Integration).where(Integration.user_id == user_id)
        )

        return list(result.scalars().all())
    
    async def get_by_user_and_platform(
            self,
            user_id: int,
            platform: str,
    )-> Integration | None:
        
        result = await self.session.execute(
            select(Integration).where(
                Integration.user_id == user_id,
                Integration.platform == platform,
            )
        )

        return result.scalar_one_or_none()
    
    async def update(
            self,
            integration_id: uuid.UUID,
            **kwargs,
    ) -> Integration | None:
        
        await self.session.execute(
            update(Integration)
            .where(Integration.id == integration_id)
            .values(**kwargs)
        )

        await self.session.commit()
        return await self.get_by_id(integration_id)

    async def save_tokens(
        self,
        integration_id: uuid.UUID,
        access_token: str,
        refresh_token: str | None,
        token_expires_at: datetime,
    ) -> None:
        await self.session.execute(
            update(Integration)
            .where(Integration.id == integration_id)
            .values(
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
            )
        )
        await self.session.commit()

    async def delete(self, integration_id: uuid.UUID) -> None:
        integration = await self.get_by_id(integration_id)
        if integration:
            await self.session.delete(integration)
            await self.session.commit()
