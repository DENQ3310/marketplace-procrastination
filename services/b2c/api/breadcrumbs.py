import fastapi
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.category import BreadcrumbResponse
from exceptions.category import CategoryHierarchyError, CategoryNotFoundError
from exceptions.product import ProductNotFoundError
from services import category_service
from core.db import get_db


router = fastapi.APIRouter(prefix="/api/v1/breadcrumbs")


@router.get("")
async def get_breadcrumbs(
	db: Annotated[AsyncSession, fastapi.Depends(get_db)],
	category_id: str | None = None,
	product_id: str | None = None,
) -> BreadcrumbResponse:
	"""Get breadcrumbs for a category or product

	Args:
		db (Annotated[AsyncSession, fastapi.Depends]): Database session
		category_id (str | None, optional): Category ID
		product_id (str | None, optional): Product ID

	Returns:
		BreadcrumbResponse: Breadcrumbs
	"""
	try:
		return await category_service.get_category_breadcrumbs(
			db, category_id, product_id
		)

	except ValueError as e:
		raise fastapi.HTTPException(
			status_code=400,
			detail={"code": "INVALID_REQUEST", "message": str(e)},
		) from e

	except (CategoryNotFoundError, ProductNotFoundError) as e:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(e)},
		) from e

	except CategoryHierarchyError as e:
		raise fastapi.HTTPException(
			status_code=422,
			detail={"code": "ORPHAN_NODE", "message": str(e)},
		) from e

	except Exception as e:
		raise fastapi.HTTPException(status_code=503, detail=str(e)) from e
