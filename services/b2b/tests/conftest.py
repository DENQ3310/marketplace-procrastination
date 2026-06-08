import os
import subprocess
from collections.abc import AsyncGenerator, AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from core import db as core_db


@pytest.fixture(scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
	"""
	Init test database and run migrations.
	"""
	with PostgresContainer("postgres:15") as pg:
		sync_url = pg.get_connection_url()
		async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
		env = os.environ.copy()
		env["DATABASE_URL"] = async_url

		subprocess.run(
			["uv", "run", "alembic", "-c", "database/alembic.ini", "upgrade", "head"],
			check=True,
			env=env,
		)  # noqa: S607

		engine = create_async_engine(async_url, echo=False)
		try:
			yield engine
		finally:
			await engine.dispose()


@pytest.fixture()
def session_factory(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
	"""
	Create session for test database.
	"""
	return async_sessionmaker(
		bind=test_engine, expire_on_commit=False, class_=AsyncSession
	)


@pytest.fixture()
async def db_session(
	session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
	"""
	Create session for test database and truncate tables.
	"""
	async with session_factory() as session:
		try:
			yield session
		finally:
			await session.execute(text("TRUNCATE TABLE catalog.categories CASCADE"))
			await session.commit()


@pytest.fixture()
def app(session_factory: async_sessionmaker[AsyncSession]) -> FastAPI:
	"""
	Create FastAPI app with override get_db dependency.
	"""

	async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
		async with session_factory() as session:
			yield session

	from main import (
		app as fastapi_app,
		http_exception_handler,
		request_validation_exception_handler,
	)

	fastapi_app.dependency_overrides[core_db.get_db] = override_get_db

	from fastapi import FastAPI, HTTPException
	from fastapi.exceptions import RequestValidationError
	from fastapi.middleware.cors import CORSMiddleware
	from api.categories import router as category_router
	from api.products import router as product_router
	from api.invoice import router as invoice_router
	from api.public_catalog import router as public_catalog_router
	from api.sku import router as sku_router
	from core.config import settings as app_settings
	from middlewares.service_key_verification import verify_service_key
	from middlewares.token_verification import verify_token

	app_settings.B2C_SERVICE_KEY = "test-b2c-service-key"

	test_app = FastAPI(debug=False)
	test_app.add_exception_handler(HTTPException, http_exception_handler)
	test_app.add_exception_handler(
		RequestValidationError, request_validation_exception_handler
	)
	test_app.middleware("http")(verify_service_key)
	test_app.middleware("http")(verify_token)
	test_app.add_middleware(
		CORSMiddleware,
		allow_origins=["http://localhost:5173", "http://localhost:3000"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)
	test_app.include_router(public_catalog_router, prefix="/api/v1")
	test_app.include_router(category_router, prefix="/api/v1")
	test_app.include_router(product_router, prefix="/api/v1")
	test_app.include_router(invoice_router, prefix="/api/v1")
	test_app.include_router(sku_router, prefix="/api/v1")
	test_app.dependency_overrides[core_db.get_db] = override_get_db

	return test_app


@pytest.fixture()
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
	"""
	Create client for test database.
	"""
	async with AsyncClient(
		transport=ASGITransport(app=app), base_url="http://test"
	) as client:
		yield client
