from pydantic_settings import BaseSettings


class settings(BaseSettings):  # noqa
	DATABASE_URL: str

	SESSION_EXPIRE_SECONDS: int
	SECRET_KEY: str
	ALGORITHM: str

	S3_ENDPOINT: str
	S3_ACCESS_KEY: str
	S3_SECRET_KEY: str
	S3_BUCKET: str
	MAX_SIZE: int

	RABBITMQ_HOST: str
	RABBITMQ_PORT: str
	RABBITMQ_USER: str
	RABBITMQ_PASSWORD: str
	RABBITMQ_EXCHANGE: str

	OUTBOX_WORKER_ENABLED: bool
	OUTBOX_POLL_INTERVAL_SECONDS: float

	B2C_SERVICE_KEY: str = ""

	model_config = {"env_file": ".env", "extra": "allow"}


settings = settings()
