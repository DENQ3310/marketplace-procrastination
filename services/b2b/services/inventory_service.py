from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud import inventory as inventory_crud
from crud import outbox as outbox_crud
from database.models.catalog.variants import Sku
from exceptions.sku import (
	SkuIdempotencyConflictError,
	SkuInsufficientStockError,
	SkuNotFoundError,
)
from schemas.inventory import (
	InventoryItemRequest,
	InventoryItemResponse,
	InventoryRequest,
	InventoryResponse,
)


def _normalize_items(items: list[InventoryItemRequest]) -> list[dict]:
	quantities: dict[UUID, int] = {}
	for item in items:
		quantities[item.sku_id] = quantities.get(item.sku_id, 0) + item.quantity
	return [
		{"sku_id": str(sku_id), "quantity": quantities[sku_id]}
		for sku_id in sorted(quantities, key=str)
	]


def _build_response(
	request: InventoryRequest,
	operation: str,
	skus: list[Sku],
) -> InventoryResponse:
	return InventoryResponse(
		idempotency_key=request.idempotency_key,
		operation=operation,
		items=[
			InventoryItemResponse(
				sku_id=sku.id,
				active_quantity=sku.active_quantity,
				reserved_quantity=sku.reserved_quantity,
			)
			for sku in skus
		],
	)


async def _apply_inventory_operation(
	db: AsyncSession,
	request: InventoryRequest,
	operation: str,
) -> InventoryResponse:
	normalized_items = _normalize_items(request.items)
	await inventory_crud.lock_idempotency_key(db, operation, request.idempotency_key)
	existing = await inventory_crud.get_operation(
		db, operation, request.idempotency_key
	)
	if existing is not None and existing.items != normalized_items:
		raise SkuIdempotencyConflictError(
			"idempotency_key was already used with a different payload"
		)

	sku_ids = [UUID(item["sku_id"]) for item in normalized_items]
	skus = await inventory_crud.lock_skus(db, sku_ids)
	if len(skus) != len(sku_ids):
		found_ids = {sku.id for sku in skus}
		missing_id = next(sku_id for sku_id in sku_ids if sku_id not in found_ids)
		raise SkuNotFoundError(f"SKU with id {missing_id} not found")

	existing = await inventory_crud.get_operation(
		db, operation, request.idempotency_key
	)
	if existing is not None:
		if existing.items != normalized_items:
			raise SkuIdempotencyConflictError(
				"idempotency_key was already used with a different payload"
			)
		return _build_response(request, operation, skus)

	quantities = {
		UUID(item["sku_id"]): int(item["quantity"]) for item in normalized_items
	}
	for sku in skus:
		quantity = quantities[sku.id]
		available = (
			sku.active_quantity if operation == "RESERVE" else sku.reserved_quantity
		)
		if available < quantity:
			raise SkuInsufficientStockError(
				f"SKU with id {sku.id} has insufficient quantity"
			)

	for sku in skus:
		quantity = quantities[sku.id]
		if operation == "RESERVE":
			sku.active_quantity -= quantity
			sku.reserved_quantity += quantity
			if sku.active_quantity == 0:
				await outbox_crud.enqueue_sku_out_of_stock_event(
					db, sku.id, sku.product_id
				)
		else:
			sku.active_quantity += quantity
			sku.reserved_quantity -= quantity
		db.add(sku)

	inventory_crud.add_operation(
		db,
		operation,
		request.idempotency_key,
		normalized_items,
	)
	await db.commit()
	for sku in skus:
		await db.refresh(sku)
	return _build_response(request, operation, skus)


async def reserve(db: AsyncSession, request: InventoryRequest) -> InventoryResponse:
	return await _apply_inventory_operation(db, request, "RESERVE")


async def unreserve(db: AsyncSession, request: InventoryRequest) -> InventoryResponse:
	return await _apply_inventory_operation(db, request, "UNRESERVE")
