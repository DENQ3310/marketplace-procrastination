from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
	name: str = Field(..., example="Электроника")
	slug: str = Field(..., example="electronics")
	description: Optional[str] = None
	parent_id: Optional[UUID] = None


class CategoryCreate(CategoryBase):
	pass


class CategoryRead(CategoryBase):
	id: UUID
	created_at: datetime
	is_active: bool

	class Config:
		from_attributes = True
