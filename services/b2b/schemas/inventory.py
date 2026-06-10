from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryItemRequest(BaseModel):
	sku_id: UUID
	quantity: int = Field(..., gt=0)


class InventoryRequest(BaseModel):
	idempotency_key: UUID
	items: list[InventoryItemRequest] = Field(..., min_length=1, max_length=100)


class InventoryItemResponse(BaseModel):
	sku_id: UUID
	active_quantity: int
	reserved_quantity: int


class InventoryResponse(BaseModel):
	idempotency_key: UUID
	operation: Literal["RESERVE", "UNRESERVE"]
	items: list[InventoryItemResponse]
