import uuid
from typing import Annotated

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from core import db
from exceptions.product import ProductNotFoundError
from exceptions.subscription import (
	InvalidSubscriptionTypeError,
	SubscriptionAlreadyExistsError,
)
from schemas.subscription import SubscribeRequest
from services import subscription_service
from fastapi.security import HTTPBearer

security = HTTPBearer()

router = fastapi.APIRouter(
	prefix="/api/v1/favorites",
	tags=["Подписка"],
	dependencies=[fastapi.Depends(security)],
)


@router.post(
	"/{product_id}/subscribe",
	status_code=204,
)
async def subscribe_to_product(
	product_id: uuid.UUID,
	http_request: fastapi.Request,
	db_session: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
	body: SubscribeRequest | None = None,
) -> fastapi.Response:
	user_id = uuid.UUID(str(getattr(http_request.state, "user_id", None)))
	request_body = body if body is not None else SubscribeRequest()
	try:
		await subscription_service.subscribe_to_product(
			db_session, user_id, product_id, request_body
		)
	except ProductNotFoundError as err:
		raise fastapi.HTTPException(
			status_code=404,
			detail={"code": "NOT_FOUND", "message": str(err)},
		) from err
	except SubscriptionAlreadyExistsError as err:
		raise fastapi.HTTPException(
			status_code=409,
			detail={"code": "SUBSCRIPTION_ALREADY_EXISTS", "message": str(err)},
		) from err
	except InvalidSubscriptionTypeError as err:
		raise fastapi.HTTPException(
			status_code=400,
			detail={"code": "INVALID_NOTIFY_ON", "message": str(err)},
		) from err
	return fastapi.Response(status_code=204)


@router.delete("/{product_id}/subscribe", status_code=204)
async def unsubscribe(
	product_id: uuid.UUID,
	http_request: fastapi.Request,
	db_session: Annotated[AsyncSession, fastapi.Depends(db.get_db)],
) -> fastapi.Response:
	user_id = uuid.UUID(str(getattr(http_request.state, "user_id", None)))
	await subscription_service.unsubscribe_from_product(db_session, user_id, product_id)
	return fastapi.Response(status_code=204)
