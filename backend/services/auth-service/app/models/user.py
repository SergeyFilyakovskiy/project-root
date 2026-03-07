"""
    Module with models for DB
"""

import datetime
from enum import StrEnum
import os
import sys

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from app.db.session import Base

class RoleEnum(StrEnum):
    
    """
    Список всех ролей в БД
    """
    
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


class Profile(Base):
    """
    Модель для всех профилей пользователей
    """

    username: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String
    )

    last_name: Mapped[str | None] = mapped_column(
        String
    )

    date_of_birth: Mapped[datetime] = mapped_column( # type: ignore
        DateTime, 
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('auth.users.id'),
        unique=True
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        uselist=False
    )

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
        String,
        nullable= False
    )

    role: Mapped[RoleEnum] = mapped_column(
        default= RoleEnum.USER,
        nullable= False
    )
    
    profile: Mapped['Profile'] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        lazy="joined",
    )
