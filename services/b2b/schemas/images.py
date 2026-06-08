from enum import Enum
from uuid import UUID
from fastapi import UploadFile
from pydantic import BaseModel


class ImageEntityTypeEnum(str, Enum):
	PRODUCT = "PRODUCT"
	SKU = "SKU"


class ImageUploadResponse(BaseModel):
	id: UUID
	url: str
	ordering: int
	entity_type: ImageEntityTypeEnum
	entity_id: UUID


class ImageUploadRequest(BaseModel):
	file: UploadFile
	entity_type: ImageEntityTypeEnum
	entity_id: UUID | None
	ordering: int | None
