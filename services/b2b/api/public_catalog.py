from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from exceptions.product import ProductNotFoundError
from schemas.public_catalog import (
	ProductPublicPaginatedResponse,
	ProductPublicResponse,
	PublicProductsBatchRequest,
	PublicSort,
)
from services import public_catalog_service

router = APIRouter(prefix="/public", tags=["Public Catalog"])


@router.get("/products", response_model=ProductPublicPaginatedResponse)
async def list_public_products(
	db: Annotated[AsyncSession, Depends(get_db)],
	limit: Annotated[int, Query(ge=1, le=100)] = 20,
	offset: Annotated[int, Query(ge=0)] = 0,
	category_id: UUID | None = None,
	search: str | None = None,
	seller_id: UUID | None = None,
	min_price: Annotated[int | None, Query(ge=0)] = None,
	max_price: Annotated[int | None, Query(ge=0)] = None,
	sort: Annotated[PublicSort, Query()] = "created_desc",
) -> ProductPublicPaginatedResponse:
	return await public_catalog_service.list_public_catalog(
		db,
		limit,
		offset,
		category_id,
		search,
		seller_id,
		min_price,
		max_price,
		sort,
	)


@router.post("/products/batch", response_model=list[ProductPublicResponse])
async def batch_public_products(
	body: PublicProductsBatchRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProductPublicResponse]:
	return await public_catalog_service.batch_public_products(db, body.product_ids)


@router.get("/products/{product_id}", response_model=ProductPublicResponse)
async def get_public_product(
	product_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductPublicResponse:
	try:
		return await public_catalog_service.get_public_product_for_b2c(db, product_id)
	except ProductNotFoundError as e:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e
