from pydantic import BaseModel, ConfigDict


class Image(BaseModel):
	url: str
	order: int


class ImageInFavorite(BaseModel):
	url: str
	ordering: int
	model_config = ConfigDict(from_attributes=True)
