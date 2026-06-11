import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request

from api.auth import router as auth_router
from api.categories import router as category_router
from api.images import router as image_router
from api.invoice import router as invoice_router
from api.inventory import router as inventory_router
from api.fulfill import router as fulfill_router
from api.moderation_events import router as moderation_events_router
from api.products import router as product_router
from api.public_catalog import router as public_catalog_router
from api.sku import router as sku_router
from core.config import settings
from middlewares.service_key_verification import verify_service_key
from middlewares.token_verification import verify_token
from services import outbox_worker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
	worker_task: asyncio.Task | None = None
	if settings.OUTBOX_WORKER_ENABLED:
		worker_task = asyncio.create_task(outbox_worker.run_forever())
		logger.info("Outbox worker task scheduled")
	yield
	if worker_task is not None:
		worker_task.cancel()
		try:
			await worker_task
		except asyncio.CancelledError:
			pass


app = FastAPI(
	title="NeoMarket B2B API",
	description="API для кабинета продавца: управление товарами и складом",
	version="1.0.0",
	lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
	detail = exc.detail
	if isinstance(detail, dict) and "code" in detail and "message" in detail:
		return JSONResponse(
			status_code=exc.status_code,
			content={
				"code": detail["code"],
				"message": detail["message"],
			},
			headers=exc.headers,
		)
	return JSONResponse(
		status_code=exc.status_code,
		content={"code": "HTTP_ERROR", "message": str(detail)},
		headers=exc.headers,
	)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
	_request: Request, exc: RequestValidationError
) -> JSONResponse:
	fields = sorted(
		{
			str(error["loc"][-1])
			for error in exc.errors()
			if error.get("loc")
		}
	)
	message = "Invalid request"
	if fields:
		message = f"Invalid request fields: {', '.join(fields)}"
	return JSONResponse(
		status_code=400,
		content={
			"code": "VALIDATION_ERROR",
			"message": message,
		},
	)


app.middleware("http")(verify_service_key)
app.middleware("http")(verify_token)
app.include_router(public_catalog_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(sku_router, prefix="/api/v1")
app.include_router(invoice_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(fulfill_router, prefix="/api/v1")
app.include_router(moderation_events_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(image_router, prefix="/api/v1")


@app.get("/")
def read_root() -> dict[str, str]:
	return {"service": "NeoMarket B2B", "status": "online", "documentation": "/docs"}
