import uuid

import fastapi
from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.session import SessionNotFoundError
from exceptions.user import (
	UserAlreadyExistsError,
	UserInvalidPasswordError,
	UserLoginConflictError,
	UserNotFoundError,
	UserPasswordTooWeakError,
)
from services import auth_service
from core import db
from schemas.user import LoginResponse, RegisterRequest, LoginRequest, SessionInfo
from pydantic import ValidationError

router = fastapi.APIRouter(prefix="/api/v1/auth", tags=["Авторизация"])
security = HTTPBearer()


@router.post("/register")
async def register(
	data: RegisterRequest,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> LoginResponse:
	try:
		return await auth_service.register(data, db)
	except UserAlreadyExistsError as e:  # noqa
		raise fastapi.HTTPException(status_code=409, detail=f"{e}") from e
	except UserPasswordTooWeakError as e:
		raise fastapi.HTTPException(
			status_code=400, detail="Password is too weak"
		) from e
	except ValueError as e:
		raise fastapi.HTTPException(status_code=400, detail=f"{e}") from e


@router.post("/login")
async def login(
	data: LoginRequest,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	x_session_id: Annotated[str | None, fastapi.Header(alias="X-Session-Id")] = None,
) -> LoginResponse:
	if x_session_id:
		try:
			uuid.UUID(x_session_id)
		except ValueError as err:
			raise fastapi.HTTPException(
				status_code=400,
				detail={
					"code": "INVALID_SESSION_ID",
					"message": "X-Session-Id must be a valid UUID",
				},
			) from err
	try:
		return await auth_service.login(data, db, x_session_id)
	except (ValidationError, UserNotFoundError, UserInvalidPasswordError) as e:  # noqa
		raise fastapi.HTTPException(status_code=400, detail="Invalid login data") from e
	except UserLoginConflictError as e:
		raise fastapi.HTTPException(status_code=409, detail=f"{e}") from e
	except Exception as e:
		raise fastapi.HTTPException(status_code=500, detail=f"{e}") from e


@router.get("/me")
async def get_session_info(
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	credentials: HTTPAuthorizationCredentials = fastapi.Depends(security),  # noqa
) -> SessionInfo:
	token = credentials.credentials
	try:
		return await auth_service.get_session_info(token, db)
	except SessionNotFoundError as e:
		raise fastapi.HTTPException(status_code=401, detail=f"{e}") from e


@router.post("/logout")
async def logout(
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	credentials: HTTPAuthorizationCredentials = fastapi.Depends(security),  # noqa
) -> None:
	token = credentials.credentials
	try:
		await auth_service.logout(token, db)
	except SessionNotFoundError as e:
		raise fastapi.HTTPException(status_code=401, detail=f"{e}") from e


@router.post("/refresh")
async def refresh(
	refresh_token: str, db: Annotated[AsyncSession, fastapi.Depends(db.get_db)]
) -> LoginResponse:
	try:
		return await auth_service.refresh_session(refresh_token, db)
	except ValueError as e:
		raise fastapi.HTTPException(status_code=400, detail=f"{e}") from e
	except SessionNotFoundError as e:
		raise fastapi.HTTPException(status_code=401, detail=f"{e}") from e
