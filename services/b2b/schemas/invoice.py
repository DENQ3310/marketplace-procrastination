from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List


class InvoiceItemCreate(BaseModel):
	sku_id: UUID
	quantity: int


class InvoiceItemResponse(BaseModel):
	id: UUID
	sku_id: UUID
	quantity: int

	model_config = ConfigDict(from_attributes=True)


class InvoiceCreate(BaseModel):
	items: List[InvoiceItemCreate]


class InvoiceResponse(BaseModel):
	id: UUID
	seller_id: UUID
	status: str
	items: List[InvoiceItemResponse]
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
	total: int
	items: List[InvoiceResponse]
