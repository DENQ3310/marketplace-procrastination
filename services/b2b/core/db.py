from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False,
	autoflush=False,
	autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async with SessionLocal() as session:
		yield session
