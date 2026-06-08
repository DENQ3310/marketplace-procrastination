import secrets
from typing import Callable

from core.config import settings
from fastapi import Request
from fastapi.responses import JSONResponse

SERVICE_KEY_PATH_PREFIX = "/api/v1/public"


async def verify_service_key(request: Request, call_next: Callable) -> JSONResponse:
	if not request.url.path.startswith(SERVICE_KEY_PATH_PREFIX):
		return await call_next(request)

	service_key = request.headers.get("X-Service-Key")
	expected = settings.B2C_SERVICE_KEY
	if (
		not service_key
		or not expected
		or not secrets.compare_digest(service_key, expected)
	):
		return JSONResponse(
			status_code=401,
			content={
				"code": "UNAUTHORIZED",
				"message": "Invalid or missing service key",
			},
		)

	return await call_next(request)
