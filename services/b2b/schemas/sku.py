from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacteristicSchema(BaseModel):
	id: Optional[UUID] = None
	name: str
	value: str

	model_config = ConfigDict(from_attributes=True)


class ImageSchema(BaseModel):
	id: Optional[UUID] = None
	url: str
	ordering: int = 0

	model_config = ConfigDict(from_attributes=True)


class ImageAttachRequest(BaseModel):
	image_id: Optional[UUID] = None
	url: str = Field(..., min_length=1)
	ordering: int = 0


class SkuImageCreate(BaseModel):
	url: str = Field(..., min_length=1)
	ordering: int = 0


class SkuImageResponse(BaseModel):
	id: UUID
	url: str
	ordering: int

	model_config = ConfigDict(from_attributes=True)


class SkuCreate(BaseModel):
	product_id: UUID
	name: str = Field(..., min_length=1, max_length=255)
	price: int = Field(..., ge=0)
	discount: int = Field(default=0, ge=0)
	cost_price: Optional[int] = Field(default=None, ge=0)
	article: Optional[str] = None
	images: List[SkuImageCreate] = Field(default_factory=list)
	characteristics: List[CharacteristicSchema] = Field(default_factory=list)


class SkuUpdate(BaseModel):
	name: Optional[str] = Field(None, min_length=1, max_length=255)
	price: Optional[int] = Field(None, ge=0)
	discount: Optional[int] = Field(None, ge=0)
	cost_price: Optional[int] = Field(None, ge=0)
	article: Optional[str] = None
	characteristics: Optional[List[CharacteristicSchema]] = None


class SkuResponse(BaseModel):
	id: UUID
	product_id: UUID
	name: str
	price: int
	discount: int = 0
	cost_price: Optional[int] = None
	stock_quantity: int = 0
	active_quantity: int = 0
	reserved_quantity: int = 0
	article: Optional[str] = None
	characteristics: List[CharacteristicSchema] = Field(default_factory=list)
	images: List[ImageSchema] = Field(default_factory=list)
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
