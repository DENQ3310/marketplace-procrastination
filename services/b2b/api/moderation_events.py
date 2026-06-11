from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from exceptions.product import ProductNotFoundError
from schemas.moderation_event import ModerationEventRequest, ModerationEventResponse
from services import moderation_event_service

router = APIRouter(prefix="/events", tags=["Moderation Events"])


@router.post("/moderation", response_model=ModerationEventResponse)
async def receive_moderation_event(
	request: ModerationEventRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ModerationEventResponse:
	try:
		return await moderation_event_service.apply_moderation_event(db, request)
	except ProductNotFoundError as exc:
		await db.rollback()
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "NOT_FOUND", "message": str(exc)},
		) from exc
