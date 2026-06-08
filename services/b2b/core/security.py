from passlib.context import CryptContext
from .config import settings
import uuid
import datetime
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: uuid.UUID) -> str:
	expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
		seconds=settings.SESSION_EXPIRE_SECONDS
	)

	data = {
		"user_id": str(user_id),
		"exp": int(expires_at.timestamp()),  # JWT требует числовой Unix timestamp
		"iat": int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
	}

	return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:

	if token.startswith("Bearer "):
		token = token[7:]

	try:
		return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	except JWTError as e:
		raise ValueError(f"Невалидный или истёкший токен: {e}") from e
