from uuid import UUID

from pydantic import BaseModel, Field

from schemas.inventory import InventoryItemRequest, InventoryItemResponse


class FulfillRequest(BaseModel):
	order_id: UUID
	items: list[InventoryItemRequest] = Field(..., min_length=1, max_length=100)


class FulfillResponse(BaseModel):
	order_id: UUID
	items: list[InventoryItemResponse]
