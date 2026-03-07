from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:

    """
    Базовый DAO класс, от которого все остальные
    DAO будут наследоваться
    """

    model = None

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        """
        Создаёт и сохраняет новую запись.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - **values - поля модели и их значения

        Возвращает:
        - model - созданный объект

        """
        new_instance = cls.model(**values)  # type: ignore
        session.add(new_instance)

        try:
            await session.commit()
            await session.refresh(new_instance)  
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return new_instance

    @classmethod
    async def find_by_id(cls, session: AsyncSession, id: int):
        """
        Находит запись по ID.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - id: int - идентификатор записи

        Возвращает:
        - model | None - объект модели или None

        """
        result = await session.execute(
            select(cls.model).where(cls.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none()

    @classmethod
    async def find_one_by(cls, session: AsyncSession, **filters):
        """
        Находит одну запись по произвольным фильтрам.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - **filters - поля модели и их значения

        Возвращает:
        - model | None - объект модели или None

        """
        query = select(cls.model)  # type: ignore
        for field, value in filters.items():
            query = query.where(getattr(cls.model, field) == value)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):
        """
        Возвращает все записи с пагинацией.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - limit: int - максимальное количество записей
        - offset: int - смещение

        Возвращает:
        - list[model] - список объектов модели

        """
        result = await session.execute(
            select(cls.model).limit(limit).offset(offset)  # type: ignore
        )
        return result.scalars().all()

    @classmethod
    async def update_by_id(
        cls,
        session: AsyncSession,
        id: int,
        data: dict,
    ):
        """
        Обновляет запись по ID.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - id: int - идентификатор записи
        - data: dict - словарь с обновляемыми полями

        Возвращает:
        - model | None - обновлённый объект или None

        """
        instance = await cls.find_by_id(session, id)
        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        try:
            await session.commit()
            await session.refresh(instance)
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return instance

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, id: int) -> bool:
        """
        Удаляет запись по ID.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - id: int - идентификатор записи

        Возвращает:
        - bool - True если запись удалена, False если не найдена

        """
        instance = await cls.find_by_id(session, id)
        if not instance:
            return False

        try:
            await session.delete(instance)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return True
