import uuid
from typing import Annotated

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from core import db
from exceptions.product import ProductNotFoundError
from schemas.catalog import PaginatedCatalogProducts
from services import favorite_service
from fastapi.security import HTTPBearer

security = HTTPBearer()

router = fastapi.APIRouter(
	prefix="/api/v1/favorites",
	tags=["Избранное"],
	dependencies=[fastapi.Depends(security)],
)


@router.get(
	"",
	response_model=PaginatedCatalogProducts,
	responses={401: {}},
)
async def get_favorites(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	limit: Annotated[int, fastapi.Query(ge=1, le=100)] = 20,
	offset: Annotated[int, fastapi.Query(ge=0)] = 0,
) -> PaginatedCatalogProducts:
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	return await favorite_service.get_favorites_list(db, user_id, limit, offset)


@router.put(
	"/{product_id}",
	status_code=204,
	responses={404: {}},
)
async def add_to_favorites(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	product_id: Annotated[uuid.UUID, fastapi.Path()],
) -> fastapi.Response:
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	try:
		await favorite_service.add_to_favorites(db, user_id, product_id)
	except ProductNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from None
	return fastapi.Response(status_code=204)


@router.delete(
	"/{product_id}",
	status_code=204,
)
async def remove_from_favorites(
	request: fastapi.Request,
	db: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	product_id: Annotated[uuid.UUID, fastapi.Path()],
) -> fastapi.Response:
	user_id = uuid.UUID(str(getattr(request.state, "user_id", None)))
	await favorite_service.remove_from_favorites(db, user_id, product_id)
	return fastapi.Response(status_code=204)
