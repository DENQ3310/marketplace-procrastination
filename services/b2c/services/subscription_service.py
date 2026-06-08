import uuid

from sqlalchemy.ext.asyncio import AsyncSession

import crud.subscription as sub_crud
from exceptions.product import ProductNotFoundError
from exceptions.subscription import InvalidSubscriptionTypeError
from schemas.subscription import SubscribeRequest, SubscriptionEvent


async def subscribe_to_product(
	db: AsyncSession,
	user_id: uuid.UUID,
	product_id: uuid.UUID,
	request: SubscribeRequest,
) -> None:
	if not request.events:
		raise InvalidSubscriptionTypeError("Events are required")

	if not await sub_crud.product_exists(db, product_id):
		raise ProductNotFoundError("Товар не найден")

	await sub_crud.create_subscription(
		db=db,
		user_id=user_id,
		product_id=product_id,
		notify_in_stock=SubscriptionEvent.BACK_IN_STOCK in request.events,
		notify_price_down=SubscriptionEvent.PRICE_DROP in request.events,
	)


async def unsubscribe_from_product(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> None:
	await sub_crud.delete_subscription_by_product(db, user_id, product_id)
