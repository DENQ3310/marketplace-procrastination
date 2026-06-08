import uuid

from pydantic import BaseModel, ConfigDict

from schemas.catalog import CatalogProductCard


class Collection(BaseModel):
	id: uuid.UUID
	name: str
	description: str = ""
	products: list[CatalogProductCard]
	model_config = ConfigDict(from_attributes=True)
