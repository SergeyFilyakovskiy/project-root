from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    
    """
    
    Базовый DAO класс, от которого все остальные
    DAO будут наследоваться
    
    """

    model = None 

    @classmethod
    async def add(cls, session: AsyncSession, **vaules):
        
        new_instance = cls.model(**vaules) # type: ignore
        session.add(new_instance)

        try:
            await session.commit()

        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        
        return new_instance
    