from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def find_one_or_none_by_id(
            self,
            data_id: int,
            session: AsyncSession
    ):
        """
        Возвращает экземпляр модели по id или None.
        """
        stmt = select(self.model).filter_by(id=data_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_one_or_none(self, session: AsyncSession, **filter_by):
        """
        Возвращает экземпляр модели по переданным параметрам или None.
        """
        stmt = select(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(
            self,
            session: AsyncSession,
            **filter_by
    ):
        """
        Возвращает все экземпляры модели соответствующие параметрам.
        """
        stmt = select(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def add(
            self,
            session: AsyncSession,
            **values
    ):
        """Создаёт экземпляр модели и возвращает её."""
        new_instance = self.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        await session.refresh(new_instance)
        return new_instance
