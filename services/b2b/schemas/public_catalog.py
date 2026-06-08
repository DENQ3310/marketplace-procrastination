from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from database.models import ProductStatusEnum
from schemas.product import CharacteristicsResponse, ProductImageResponse

PublicSort = Literal["price_asc", "price_desc", "created_desc", "popular"]


class SkuPublicResponse(BaseModel):
	id: UUID
	product_id: UUID
	name: str
	price: int
	discount: int
	stock_quantity: int
	active_quantity: int
	article: str | None = None
	images: list[ProductImageResponse] = []
	characteristics: list[CharacteristicsResponse] = []

	model_config = ConfigDict(from_attributes=True)


class ProductPublicShortResponse(BaseModel):
	id: UUID
	title: str
	slug: str
	status: ProductStatusEnum
	category_id: UUID
	min_price: int
	cover_image: str | None = None
	created_at: datetime


class ProductPublicResponse(BaseModel):
	id: UUID
	seller_id: UUID
	category_id: UUID
	title: str
	slug: str
	description: str
	status: ProductStatusEnum
	images: list[ProductImageResponse]
	characteristics: list[CharacteristicsResponse]
	skus: list[SkuPublicResponse]
	created_at: datetime
	updated_at: datetime


class ProductPublicPaginatedResponse(BaseModel):
	items: list[ProductPublicShortResponse]
	total_count: int
	limit: int
	offset: int


class PublicProductsBatchRequest(BaseModel):
	product_ids: list[UUID] = Field(..., max_length=100)
