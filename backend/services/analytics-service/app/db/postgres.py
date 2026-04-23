from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings


#движок для работы с бд
async_engine = create_async_engine(settings.get_db_async_url())

#Фабрика сессий для взаимодействия с БД
async_session = async_sessionmaker(
    autoflush=False,
    autocommit= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False,
)

async def get_postgres_connection():
    """
    Генератор для подключения к Postgres

    Передает:
    - session - Сессия в postgres
    """
    async with async_session() as session:
        try:        
            yield session
        except Exception as e:
            await session.rollback()
            raise e     
        finally: 
            await session.aclose()


async def get_postgres():
    try:
        session = async_session()
        return session
    except Exception as e:
        raise e
    finally:
        await session.aclose()