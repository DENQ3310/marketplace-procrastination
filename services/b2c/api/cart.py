import uuid
from typing import Annotated, Optional

import fastapi
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core import db
from exceptions.cart import (
	CartItemNotFoundError,
	InsufficientStockError,
	SkuUnavailableError,
)
from exceptions.sku import SkuNotFoundError
from schemas.cart import (
	CartItemAddRequest,
	CartItemQuantityUpdate,
	CartResponse,
	CartValidationResponse,
)
from services import cart_service


async def cart_session_header(
	x_session_id: Annotated[str | None, fastapi.Header(alias="X-Session-Id")] = None,
) -> Optional[JSONResponse]:
	if not x_session_id:
		return JSONResponse(
			status_code=400,
			content={
				"code": "MISSING_SESSION_ID",
				"message": "Header X-Session-Id is required",
			},
		)
	return None


router = fastapi.APIRouter(
	prefix="/api/v1/cart",
	tags=["Корзина"],
	dependencies=[fastapi.Depends(cart_session_header)],
)


def _get_cart_identity(
	request: fastapi.Request,
) -> tuple[Optional[uuid.UUID], Optional[str]]:
	user_id_raw = getattr(request.state, "user_id", None)
	session_id = getattr(request.state, "session_id", None)
	user_id = uuid.UUID(str(user_id_raw)) if user_id_raw else None
	return user_id, session_id


@router.get("", response_model=CartResponse)
async def get_cart(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartResponse:
	user_id, session_id = _get_cart_identity(request)
	return await cart_service.get_cart(db, user_id, session_id)


@router.delete("", status_code=204)
async def clear_cart(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> None:
	user_id, session_id = _get_cart_identity(request)
	await cart_service.clear_cart(db, user_id, session_id)


@router.post("/items", response_model=CartResponse)
async def add_cart_item(
	request: fastapi.Request,
	body: CartItemAddRequest,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartResponse:
	user_id, session_id = _get_cart_identity(request)
	try:
		return await cart_service.add_cart_item(
			db, user_id, session_id, body.sku_id, body.quantity
		)
	except SkuNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except SkuUnavailableError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except InsufficientStockError as err:
		raise fastapi.HTTPException(
			status_code=409,
			detail={"code": "INSUFFICIENT_STOCK", "message": str(err)},
		) from err


@router.patch("/items/{sku_id}", response_model=CartResponse)
async def update_cart_item(
	request: fastapi.Request,
	sku_id: uuid.UUID,
	body: CartItemQuantityUpdate,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartResponse:
	user_id, session_id = _get_cart_identity(request)
	try:
		return await cart_service.update_cart_item_quantity(
			db, user_id, session_id, sku_id, body.quantity
		)
	except CartItemNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except SkuNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except SkuUnavailableError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except InsufficientStockError as err:
		raise fastapi.HTTPException(
			status_code=409,
			detail={"code": "INSUFFICIENT_STOCK", "message": str(err)},
		) from err


@router.delete("/items/{sku_id}", response_model=CartResponse)
async def delete_cart_item(
	request: fastapi.Request,
	sku_id: uuid.UUID,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartResponse:
	user_id, session_id = _get_cart_identity(request)
	try:
		return await cart_service.remove_cart_item(db, user_id, session_id, sku_id)
	except CartItemNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err


@router.post("/validate", response_model=CartValidationResponse)
async def validate_cart(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartValidationResponse:
	user_id, session_id = _get_cart_identity(request)
	return await cart_service.validate_cart(db, user_id, session_id)


@router.post("/merge", response_model=CartResponse, responses={401: {}})
async def merge_cart(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> CartResponse:
	user_id = uuid.UUID(str(request.state.user_id))
	session_id = str(request.state.session_id)
	return await cart_service.merge_guest_cart(db, user_id, session_id)
