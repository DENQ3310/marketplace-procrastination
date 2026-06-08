from schemas.images import ImageUploadRequest, ImageUploadResponse
from core import s3
from minio import Minio
from database.models import Image
import crud.images as images_crud
from sqlalchemy.ext.asyncio import AsyncSession


async def post_image(
	data: ImageUploadRequest, s3_client: Minio, db: AsyncSession
) -> ImageUploadResponse:
	file_path = f"{'p' if data.entity_type == 'PRODUCT' else 's'}-{data.entity_id}-{data.file.filename}"
	s3.upload_file(data.file, file_path, s3_client)
	url = f"/api/v1/images/{file_path}"
	image = Image(
		entity_type=data.entity_type,
		url=url,
		ordering=data.ordering,
		entity_id=data.entity_id,
	)
	image = await images_crud.add_image(image, db)

	return ImageUploadResponse(
		id=image.id,
		url=image.url,
		ordering=image.ordering,
		entity_type=image.entity_type,
		entity_id=image.entity_id,
	)
