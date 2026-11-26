from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from habrareader.data.model import Base


def create_database_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or f"sqlite+aiosqlite:///{SQLITE_CONNECTION}"
    return create_async_engine(url, future=True)


async def initialize_database(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
