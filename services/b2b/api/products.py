import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from exceptions.product import (
	ProductAlreadyDeletedError,
	ProductForbiddenError,
	ProductNotFoundError,
	ProductNotOwnerError,
)
from schemas.product import (
	ProductCreate,
	ProductDetailResponse,
	ProductResponse,
	ProductSellerRead,
	ProductUpdate,
)
from schemas.sku import SkuResponse
from services import product_service
from services import sku_service

router = APIRouter(prefix="/products", tags=["B2B Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
	request: Request,
	product_in: ProductCreate,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductResponse:
	seller_id = uuid.UUID(str(request.state.user_id))
	return await product_service.create_new_product(db, product_in, seller_id)


@router.get("/", response_model=list[ProductSellerRead])
async def get_my_products(
	request: Request,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProductSellerRead]:
	seller_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	products = await product_service.get_all_seller_products(db, seller_id)
	return [ProductSellerRead.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
	request: Request,
	product_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductDetailResponse:
	seller_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await product_service.get_product_for_seller(db, product_id, seller_id)
	except ProductNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e


@router.get("/{product_id}/skus", response_model=list[SkuResponse])
async def get_product_skus(
	request: Request,
	product_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SkuResponse]:
	seller_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await sku_service.get_skus_by_product_id(db, product_id, seller_id)
	except ProductNotFoundError as e:
		raise HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
	request: Request,
	product_id: UUID,
	product_in: ProductUpdate,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductResponse:
	seller_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await product_service.update_existing_product(
			db, product_id, seller_id, product_in
		)
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
	except ProductForbiddenError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "FORBIDDEN", "message": str(e)},
		) from e


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
	request: Request,
	product_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
	seller_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		return await product_service.remove_product(db, product_id, seller_id)
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
	except ProductForbiddenError as e:
		raise HTTPException(
			status_code=403,
			detail={"code": "FORBIDDEN", "message": str(e)},
		) from e
	except ProductAlreadyDeletedError as e:
		raise HTTPException(
			status_code=400,
			detail={"code": "ALREADY_DELETED", "message": str(e)},
		) from e
