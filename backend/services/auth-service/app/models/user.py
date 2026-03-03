"""
    Module with models for DB
"""

import enum

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from ..db.session import Base

class RoleEnum(str, enum.Enum):
    
    """
    Список всех ролей в БД
    """
    
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'

class User(Base):
    
    """
    Модель для всех пользователей системы
    """

    email: Mapped[str] = mapped_column(
        String,
        unique= True,
        nullable= False
    )

    hashed_password: Mapped[str] = mapped_column(
        nullable= False
    )

    role: Mapped[RoleEnum] = mapped_column(
        default= RoleEnum.USER,
        nullable= False
    )
    
    profile_id: Mapped[int] = mapped_column(
        ForeignKey('profiles.id')
    )
    
    profile: Mapped['Profile'] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        lazy="joined",
    )

class Profile(Base):
    """
    Модель для всех профилей пользователей
    """

    username: Mapped[str] = mapped_column(
        nullable=False,
    )

    first_name: Mapped[str]

    last_name: Mapped[str | None]

    date_of_birth: Mapped[DateTime] = mapped_column(
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        uselist=False
    )
