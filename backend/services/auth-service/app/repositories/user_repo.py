from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_dao import BaseDAO
from app.models.user import User, Profile, RoleEnum


class UserDAO(BaseDAO):

    model = User

    @classmethod
    async def add_user_with_profile(
        cls,
        session: AsyncSession,
        user_data: dict,
    ) -> User:
        """
        Добавляет пользователя и привязанный к нему профиль.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - user_data: dict - словарь с данными пользователя и профиля

        Возвращает:
        - User - объект пользователя

        """

        user = cls.model(
            email=user_data['email'],
            hashed_password=user_data['hashed_password'],
        )
        session.add(user)

        try:
            await session.flush()  # получаем user.id без коммита

            profile = Profile(
                user_id=user.id,
                username=user_data['username'],
                date_of_birth=user_data['date_of_birth'],
                first_name=user_data['first_name'],
                last_name=user_data.get('last_name'),
            )
            session.add(profile)
            await session.commit()
            await session.refresh(user)

        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return user

    @classmethod
    async def find_by_email(
        cls,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """
        Находит пользователя по email с подгрузкой профиля.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - email: str - email пользователя

        Возвращает:
        - User | None - объект пользователя или None

        """
        result = await session.execute(
            select(cls.model)
            .where(cls.model.email == email)
            .options(joinedload(cls.model.profile))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def exists_by_email(
        cls,
        session: AsyncSession,
        email: str,
    ) -> bool:
        """
        Проверяет существует ли пользователь с таким email.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - email: str - email для проверки

        Возвращает:
        - bool - True если пользователь существует

        """
        result = await session.execute(
            select(cls.model.id).where(cls.model.email == email)
        )
        return result.scalar_one_or_none() is not None

    @classmethod
    async def update_role(
        cls,
        session: AsyncSession,
        user_id: int,
        role: RoleEnum,
    ) -> User | None:
        """
        Обновляет роль пользователя.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - user_id: int - ID пользователя
        - role: RoleEnum - новая роль

        Возвращает:
        - User | None - обновлённый объект или None

        """
        return await cls.update_by_id(session, user_id, {"role": role})

    @classmethod
    async def update_password(
        cls,
        session: AsyncSession,
        user_id: int,
        hashed_password: str,
    ) -> User | None:
        """
        Обновляет хэш пароля пользователя.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - user_id: int - ID пользователя
        - hashed_password: str - новый хэш пароля

        Возвращает:
        - User | None - обновлённый объект или None

        """
        return await cls.update_by_id(
            session, user_id, {"hashed_password": hashed_password}
        )


class ProfileDAO(BaseDAO):

    model = Profile

    @classmethod
    async def find_by_username(
        cls,
        session: AsyncSession,
        username: str,
    ) -> Profile | None:
        """
        Находит профиль по username.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - username: str - имя пользователя

        Возвращает:
        - Profile | None - объект профиля или None

        """
        result = await session.execute(
            select(cls.model).where(cls.model.username == username)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def find_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> Profile | None:
        """
        Находит профиль по ID пользователя.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - user_id: int - ID пользователя

        Возвращает:
        - Profile | None - объект профиля или None

        """
        result = await session.execute(
            select(cls.model).where(cls.model.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def update_profile(
        cls,
        session: AsyncSession,
        profile_id: int,
        data: dict,
    ) -> Profile | None:
        """
        Обновляет данные профиля, игнорируя None значения.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - profile_id: int - ID профиля
        - data: dict - словарь с обновляемыми полями

        Возвращает:
        - Profile | None - обновлённый профиль или None

        """
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return await cls.update_by_id(session, profile_id, filtered_data)
