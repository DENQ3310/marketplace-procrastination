from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, Depends
import uuid
from schemas.images import ImageEntityTypeEnum, ImageUploadResponse, ImageUploadRequest
import services.images_service as images_service
from core.s3 import get_s3_client
from minio import Minio
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("")
async def post_image(
	file: UploadFile,
	entity_type: ImageEntityTypeEnum,
	entity_id: uuid.UUID | None,
	ordering: int | None,
	s3_client: Annotated[Minio, Depends(get_s3_client)],
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ImageUploadResponse:
	try:
		return await images_service.post_image(
			ImageUploadRequest(
				file=file,
				entity_type=entity_type,
				entity_id=entity_id,
				ordering=ordering,
			),
			s3_client,
			db,
		)
	except Exception as e:
		raise HTTPException(status_code=418, detail=f"{e}") from e
