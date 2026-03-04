from base_dao import BaseDAO
from app.models.user import User, Profile
from sqlalchemy.ext.asyncio import AsyncSession

class UserDAO(BaseDAO):

    model = User

    @classmethod
    async def add_user_with_profile(
        cls, 
        session: AsyncSession, 
        user_data: dict
        )-> User:
        
        """
        
        Добавляет пользователя и привязанный к нему профиль.

        Аргументы:
        - session: AsyncSession - асинхронная сессия базы данных
        - user_data: dict - словарь с данными пользователя и профиля

        Возвращает:
        - User - объект пользователя

        """
        
        user = cls.model(
            email =  user_data['email'],
            hashed_password = user_data['password'],
        )

        session.add(user)
        await session.flush()

        profile = Profile(
            user_id = user.id,
            username = user_data['username'],
            date_of_birth = user_data['date_of_birth'],
            first_name = user_data['first_name'],
            last_name = user_data['last_name'],
        )

        session.add(profile)

        await session.commit()

        return user


class ProfileDAO(BaseDAO):

    model = Profile