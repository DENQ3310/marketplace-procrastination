from pydantic import BaseModel, EmailStr, Field
import datetime
import uuid
from typing import Annotated


class LoginResponse(BaseModel):
	access_token: str
	refresh_token: str
	expires_in: int
	token_type: str


class RegisterRequest(BaseModel):
	username: Annotated[str, Field(min_length=3, max_length=10)]
	email: EmailStr
	password: str


class SessionData(BaseModel):
	session_id: uuid.UUID
	user_id: uuid.UUID
	token: str
	refresh_token: str
	issued_at: datetime.datetime
	expires_in: int


class LoginRequest(BaseModel):
	email: (
		str | None
	)  # EmailStr could be used but it causes ValidationError when no email is provided
	# Solution is custom validation
	username: str | None
	password: str | None


class SessionInfo(BaseModel):
	user_id: uuid.UUID
	username: str
	email: EmailStr
	session_id: str
	issued_at: datetime.datetime
	expires_at: datetime.datetime
