from redis.asyncio import StrictRedis
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


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    created_at: Mapped[datetime] = mapped_column(server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default = func.now(), onupdate = func.now())


engine = create_async_engine(url = settings.DATABASE_URL_AIOMYSQL)
async_session_maker = async_sessionmaker(engine, class_ = AsyncSession, expire_on_commit = False)

redis = StrictRedis.from_url(settings.DATABASE_URL_AIOREDIS, decode_responses = True)
