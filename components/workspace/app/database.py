from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = None
async_session = None


def init_db():
    global engine, async_session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    if async_session is None:
        init_db()
    async with async_session() as session:
        yield session


async def dispose_db():
    global engine
    if engine:
        await engine.dispose()
