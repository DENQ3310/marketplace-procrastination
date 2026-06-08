import uuid
from typing import Callable, Optional

import crud.session as session_crud
from core.db import get_db
from core.security import decode_access_token
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError

PRIVATE_PATHS = ["/api/v1/auth/me", "/api/v1/auth/logout"]
PRIVATE_PATHS_PREFIXES = ["/api/v1/favorites", "/api/v1/orders"]
CART_PATH_PREFIX = "/api/v1/cart"
CART_MERGE_PATH = "/api/v1/cart/merge"


def _validate_session_id(session_id: str) -> Optional[JSONResponse]:
	try:
		uuid.UUID(session_id)
	except ValueError:
		return JSONResponse(
			status_code=400,
			content={
				"code": "INVALID_SESSION_ID",
				"message": "X-Session-Id must be a valid UUID",
			},
		)
	return None


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


async def _resolve_cart_identity(request: Request) -> Optional[JSONResponse]:
	path = request.url.path
	x_session_id = request.headers.get("X-Session-Id")

	if path == CART_MERGE_PATH:
		auth_error = await _authenticate_bearer(request)
		if auth_error is not None:
			return auth_error
		if not getattr(request.state, "user_id", None):
			return JSONResponse(
				status_code=401,
				content={
					"code": "UNAUTHORIZED",
					"message": "Missing or invalid Authorization header",
				},
			)
		if not x_session_id:
			return JSONResponse(
				status_code=400,
				content={
					"code": "MISSING_SESSION_ID",
					"message": "Header X-Session-Id is required",
				},
			)
		session_error = _validate_session_id(x_session_id)
		if session_error is not None:
			return session_error
		request.state.session_id = x_session_id
		return None

	auth_header = request.headers.get("Authorization")
	if auth_header and auth_header.startswith("Bearer "):
		auth_error = await _authenticate_bearer(request)
		if auth_error is not None:
			return JSONResponse(
				status_code=401,
				content={"code": "UNAUTHORIZED", "message": "Invalid or expired token"},
			)
		request.state.session_id = None
		return None

	if x_session_id:
		session_error = _validate_session_id(x_session_id)
		if session_error is not None:
			return session_error
		request.state.user_id = None
		request.state.session_id = x_session_id
		return None

	return JSONResponse(
		status_code=400,
		content={
			"code": "MISSING_CART_IDENTITY",
			"message": "Provide Authorization or X-Session-Id header",
		},
	)


async def verify_token(request: Request, call_next: Callable) -> JSONResponse:
	if request.url.path.startswith(CART_PATH_PREFIX):
		cart_error = await _resolve_cart_identity(request)
		if cart_error is not None:
			return cart_error
		return await call_next(request)

	if request.url.path not in PRIVATE_PATHS and not any(
		request.url.path.startswith(prefix) for prefix in PRIVATE_PATHS_PREFIXES
	):
		return await call_next(request)

	auth_error = await _authenticate_bearer(request)
	if auth_error is not None:
		return auth_error

	return await call_next(request)
