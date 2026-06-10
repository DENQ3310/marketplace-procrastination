from typing import Callable, Optional

import crud.session as session_crud
from core.db import get_db
from core.security import decode_access_token
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError

PRIVATE_PATHS: list[str] = []
PRIVATE_PATHS_PREFIXES = ["/api/v1/products", "/api/v1/skus", "/api/v1/invoices"]


async def _authenticate_bearer(request: Request) -> Optional[JSONResponse]:
	auth_header = request.headers.get("Authorization")
	if not auth_header or not auth_header.startswith("Bearer "):
		return JSONResponse(
			status_code=401,
			content={
				"code": "UNAUTHORIZED",
				"message": "Missing or invalid Authorization header",
			},
		)

	token = auth_header.split(" ", 1)[1]

	try:
		decoded = decode_access_token(token)
		request.state.user_id = decoded.get("user_id")
	except JWTError:
		return JSONResponse(
			status_code=401,
			content={"code": "UNAUTHORIZED", "message": "Invalid or expired token"},
		)
	except ValueError as err:
		return JSONResponse(
			status_code=401, content={"code": "UNAUTHORIZED", "message": str(err)}
		)

	get_db_dep = request.app.dependency_overrides.get(get_db, get_db)
	async for db in get_db_dep():
		is_active = await session_crud.check_active_session(token, db)
		if not is_active:
			return JSONResponse(
				status_code=401,
				content={"code": "UNAUTHORIZED", "message": "Token invalidated in db"},
			)
		break

	return None


async def verify_token(request: Request, call_next: Callable) -> JSONResponse:
	if request.method == "GET" and request.url.path == "/api/v1/products":
		return await call_next(request)
	if request.url.path not in PRIVATE_PATHS and not any(
		request.url.path.startswith(prefix) for prefix in PRIVATE_PATHS_PREFIXES
	):
		return await call_next(request)

	auth_error = await _authenticate_bearer(request)
	if auth_error is not None:
		return auth_error

	return await call_next(request)
