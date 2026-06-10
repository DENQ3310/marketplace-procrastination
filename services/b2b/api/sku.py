import uuid
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from exceptions.product import ProductNotFoundError, ProductNotOwnerError
from exceptions.sku import (
	SkuForbiddenError,
	SkuNotFoundError,
	SkuValidationError,
)
from schemas.sku import (
	ImageAttachRequest,
	SkuCreate,
	SkuImageResponse,
	SkuResponse,
	SkuUpdate,
)
from services import sku_service

router = APIRouter(prefix="/skus", tags=["SKU"])


@router.post("", response_model=SkuResponse, status_code=201)
async def create_sku_endpoint(
	request: Request,
	data: SkuCreate,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> SkuResponse:
	"""Create a new SKU entry."""
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.create_sku(db, data, user_id)
	except ProductNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
	except ProductNotOwnerError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "NOT_OWNER", "message": str(e)},
		) from e
	except SkuForbiddenError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "FORBIDDEN", "message": str(e)},
		) from e
	except SkuValidationError as e:
		raise HTTPException(
			status_code=400,
			detail={"code": "INVALID_REQUEST", "message": str(e)},
		) from e


@router.post(
	"/{sku_id}/images",
	response_model=SkuImageResponse,
	status_code=201,
)
async def attach_sku_image_endpoint(
	request: Request,
	sku_id: UUID,
	data: ImageAttachRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> SkuImageResponse:
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.attach_sku_image(db, sku_id, data, user_id)
	except SkuNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
	except ProductNotOwnerError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "NOT_OWNER", "message": str(e)},
		) from e
	except SkuForbiddenError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "FORBIDDEN", "message": str(e)},
		) from e
	except SkuValidationError as e:
		raise HTTPException(
			status_code=400,
			detail={"code": "INVALID_REQUEST", "message": str(e)},
		) from e


@router.put("/{sku_id}", response_model=SkuResponse)
@router.patch("/{sku_id}", response_model=SkuResponse)
async def update_sku_endpoint(
	request: Request,
	sku_id: UUID,
	data: SkuUpdate,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> SkuResponse:
	"""Update an existing SKU by its ID."""
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.update_sku(
			db, sku_id, data.model_dump(exclude_unset=True), user_id
		)
	except SkuNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
	except ProductNotOwnerError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "NOT_OWNER", "message": str(e)},
		) from e
	except SkuForbiddenError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "FORBIDDEN", "message": str(e)},
		) from e


@router.get("/{sku_id}", response_model=SkuResponse)
async def get_sku_endpoint(
	request: Request,
	sku_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> SkuResponse:
	"""Retrieve detailed information about a specific SKU by its unique identifier."""
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.get_sku(db, sku_id, user_id)
	except SkuNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
	except ProductNotOwnerError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "NOT_OWNER", "message": str(e)},
		) from e


@router.get("/product/{product_id}", response_model=List[SkuResponse])
async def get_skus_by_product_endpoint(
	request: Request,
	product_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SkuResponse]:
	"""Retrieve all SKUs associated with a specific product ID."""
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.get_skus_by_product_id(db, product_id, user_id)
	except ProductNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
