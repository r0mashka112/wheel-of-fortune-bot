from app.config import settings
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

engine = create_async_engine(url = settings.DATABASE_URL_AIOMYSQL)
async_session_maker = async_sessionmaker(engine, class_ = AsyncSession, expire_on_commit = False)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    created_at: Mapped[datetime] = mapped_column(server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default = func.now(), onupdate = func.now())