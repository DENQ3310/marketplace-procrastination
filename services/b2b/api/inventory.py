from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from exceptions.sku import (
	SkuIdempotencyConflictError,
	SkuInsufficientStockError,
	SkuNotFoundError,
)
from schemas.inventory import InventoryRequest, InventoryResponse
from services import inventory_service

router = APIRouter(tags=["Inventory"])


async def _execute(
	db: AsyncSession,
	request: InventoryRequest,
	operation: str,
) -> InventoryResponse:
	try:
		if operation == "RESERVE":
			return await inventory_service.reserve(db, request)
		return await inventory_service.unreserve(db, request)
	except SkuNotFoundError as exc:
		await db.rollback()
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "NOT_FOUND", "message": str(exc)},
		) from exc
	except (SkuInsufficientStockError, SkuIdempotencyConflictError) as exc:
		await db.rollback()
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail={"code": "INVENTORY_CONFLICT", "message": str(exc)},
		) from exc


@router.post("/reserve", response_model=InventoryResponse)
async def reserve(
	request: InventoryRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
	return await _execute(db, request, "RESERVE")


@router.post("/unreserve", response_model=InventoryResponse)
async def unreserve(
	request: InventoryRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> InventoryResponse:
	return await _execute(db, request, "UNRESERVE")
