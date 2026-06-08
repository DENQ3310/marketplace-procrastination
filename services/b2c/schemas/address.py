import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AddressResponse(BaseModel):
	country: str = Field(max_length=100)
	region: str | None = Field(default=None, max_length=200)
	city: str = Field(max_length=200)
	street: str = Field(max_length=200)
	building: str = Field(max_length=50)
	apartment: str | None = Field(default=None, max_length=50)
	postal_code: str | None = Field(default=None, max_length=20)
	recipient_name: str | None = Field(default=None, max_length=200)
	recipient_phone: str | None = None
	is_default: bool = False
	comment: str | None = Field(default=None, max_length=500)

	id: uuid.UUID
	created_at: datetime
