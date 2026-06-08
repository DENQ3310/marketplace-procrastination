from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.category import CategoryCreate, CategoryRead
from services import category_service
from uuid import UUID

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
	category_in: CategoryCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> CategoryRead:
	return await category_service.create_new_category(db, category_in)


@router.get("/", response_model=list[CategoryRead])
async def get_categories(
	db: Annotated[AsyncSession, Depends(get_db)],
	parent_id: UUID | None = None,
) -> list[CategoryRead]:
	return await category_service.list_categories(db, parent_id)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
	category_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
) -> CategoryRead:
	return await category_service.get_category_or_404(db, category_id)
