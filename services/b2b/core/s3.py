from fastapi import UploadFile
from minio import Minio
from core.config import settings
from exceptions.s3 import S3FileTooBigError, S3UnallowedFileTypeError

ALLOWED_FILE_TYPES = ["jpeg", "jpg", "png"]


def get_s3_client() -> Minio:
	client = Minio(
		endpoint=settings.S3_ENDPOINT,
		access_key=settings.S3_ACCESS_KEY,
		secret_key=settings.S3_SECRET_KEY,
		secure=False,
	)

	if not client.bucket_exists(settings.S3_BUCKET):
		client.make_bucket(settings.S3_BUCKET)

	return client


def upload_file(file: UploadFile, filename: str, client: Minio) -> None:
	if not file.content_type not in ALLOWED_FILE_TYPES:
		raise S3UnallowedFileTypeError

	if file.size > settings.MAX_SIZE:
		raise S3FileTooBigError

	client.put_object(
		settings.S3_BUCKET, data=file.file, object_name=filename, length=file.size
	)
