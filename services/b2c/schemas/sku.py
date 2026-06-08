import uuid
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from schemas.characteristic import Characteristic, CharacteristicInFavorite
from schemas.image import Image


class Sku(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: uuid.UUID
	name: str
	price: float
	quantity: int = Field(alias="active_quantity")
	characteristics: list[Characteristic]
	images: list[Image]


class SkuShort(BaseModel):
	name: str
	price: float
	image: Image


class SkuInFavorite(BaseModel):
	id: uuid.UUID
	name: str
	price: int
	active_quantity: int
	characteristics: List[CharacteristicInFavorite] = []
	model_config = ConfigDict(from_attributes=True)
