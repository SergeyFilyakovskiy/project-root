import uuid
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_job import SyncJob
from app.messaging.schemas import SyncStatus


class SyncJobRepo:
    """
    Репозиторий для управления задачами синхронизации.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        integration_id: uuid.UUID,
        platform: str,
        date_from: datetime,
        date_to: datetime,
    ) -> SyncJob:
        """Создаёт новую задачу синхронизации со статусом PENDING."""
        job = SyncJob(
            integration_id=integration_id,
            platform=platform,
            date_from=date_from,
            date_to=date_to,
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> SyncJob | None:
        """Возвращает задачу по ID."""
        result = await self.session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def set_status(
        self,
        job_id: uuid.UUID,
        status: SyncStatus,
        error: str | None = None,
    ) -> None:
        """Обновляет статус задачи и опционально записывает ошибку."""
        await self.session.execute(
            update(SyncJob)
            .where(SyncJob.id == job_id)
            .values(status=status, error=error)
        )
        await self.session.commit()

    async def get_pending(self) -> list[SyncJob]:
        """
        Возвращает все задачи в статусе PENDING.
        Используется scheduler'ом для отправки в очередь.
        """
        result = await self.session.execute(
            select(SyncJob).where(SyncJob.status == SyncStatus.PENDING)
        )
        return list(result.scalars().all())

    async def update_data(
            self,
            data: dict,
            job_id: uuid.UUID
            ):
        await self.session.execute(
            update(SyncJob)
            .where(SyncJob.id == job_id)
            .values(raw_data=data)
        )
        await self.session.commit()