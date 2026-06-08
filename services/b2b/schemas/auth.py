from pydantic import BaseModel, EmailStr, Field
import uuid
from typing import Annotated


class SellerCreate(BaseModel):
	email: EmailStr
	password: str
	first_name: Annotated[str, Field(min_length=3, max_length=15)]
	last_name: Annotated[str, Field(min_length=3, max_length=15)]
	middle_name: Annotated[str, Field(min_length=3, max_length=15)] | None
	company_name: Annotated[str, Field(min_length=3, max_length=50)]
	phone: str | None  # Do we neew validation for this?


class TokenResponse(BaseModel):
	user_id: uuid.UUID
	access_token: str
	refresh_token: str
	token_type: str
	expires_in: int


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class RefreshRequest(BaseModel):
	refresh_token: str
