from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_maker
from app.core.decorators import handle_db_errors


class BaseDAO:
    model = None

    @classmethod
    @handle_db_errors
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    @handle_db_errors
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    @handle_db_errors
    async def create(cls, **values):
        async with async_session_maker() as session:
            new_instance = cls.model(**values)
            session.add(new_instance)

            try:
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error

            await session.refresh(new_instance)
            return new_instance

    @classmethod
    @handle_db_errors
    async def update(cls, values: dict, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            obj = result.scalar_one_or_none()

            if obj:
                for key, value in values.items():
                    setattr(obj, key, value)

                await session.commit()
                await session.refresh(obj)
                return obj
            else:
                raise ValueError("Object not found")
