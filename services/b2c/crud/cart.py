import uuid
from typing import Optional

from sqlalchemy import Result, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.cart.item import CartItem
from database.models.catalog.base import Product
from database.models.catalog.variants import Image, Sku


async def get_cart_items_with_details(
	db: AsyncSession, user_id: Optional[uuid.UUID], session_id: Optional[str]
) -> list[tuple[CartItem, Sku, Product, Optional[Image]]]:
	query = (
		select(CartItem, Sku, Product)
		.join(Sku, CartItem.sku_id == Sku.id)
		.join(Product, Sku.product_id == Product.id)
		.options(
			selectinload(Sku.images),
			selectinload(Product.images),
		)
	)

	if user_id:
		query = query.where(CartItem.user_id == user_id)
	elif session_id:
		query = query.where(CartItem.session_id == session_id)

	result: Result = await db.execute(query)
	rows = result.all()

	enriched_items = []
	for cart_item, sku, product in rows:
		image = None
		if sku.images:
			image = sorted(sku.images, key=lambda img: img.ordering)[0]
		elif product.images:
			image = sorted(product.images, key=lambda img: img.ordering)[0]
		enriched_items.append((cart_item, sku, product, image))

	return enriched_items


async def clear_cart(
	db: AsyncSession, user_id: Optional[uuid.UUID], session_id: Optional[str]
) -> None:
	query = delete(CartItem)

	if user_id:
		query = query.where(CartItem.user_id == user_id)
	elif session_id:
		query = query.where(CartItem.session_id == session_id)

	await db.execute(query)
	await db.commit()


async def get_sku_by_id(db: AsyncSession, sku_id: uuid.UUID) -> Optional[Sku]:
	result: Result = await db.execute(
		select(Sku).where(Sku.id == sku_id).options(selectinload(Sku.product))
	)
	return result.scalar_one_or_none()


async def get_cart_item_by_sku(
	db: AsyncSession,
	user_id: Optional[uuid.UUID],
	session_id: Optional[str],
	sku_id: uuid.UUID,
) -> Optional[CartItem]:
	query = select(CartItem).where(CartItem.sku_id == sku_id)

	if user_id:
		query = query.where(CartItem.user_id == user_id)
	elif session_id:
		query = query.where(CartItem.session_id == session_id)

	result: Result = await db.execute(query)
	return result.scalar_one_or_none()


async def create_cart_item(
	db: AsyncSession,
	user_id: Optional[uuid.UUID],
	session_id: Optional[str],
	sku_id: uuid.UUID,
	quantity: int,
	unit_price_at_add: int,
) -> CartItem:
	cart_item = CartItem(
		user_id=user_id,
		session_id=session_id,
		sku_id=sku_id,
		quantity=quantity,
		unit_price_at_add=unit_price_at_add,
	)
	db.add(cart_item)
	await db.commit()
	await db.refresh(cart_item)
	return cart_item


async def update_cart_item_quantity(
	db: AsyncSession, cart_item: CartItem, quantity: int
) -> CartItem:
	cart_item.quantity = quantity
	await db.commit()
	await db.refresh(cart_item)
	return cart_item


async def delete_cart_item(db: AsyncSession, cart_item: CartItem) -> None:
	await db.delete(cart_item)
	await db.commit()


async def get_guest_cart_items(db: AsyncSession, session_id: str) -> list[CartItem]:
	result: Result = await db.execute(
		select(CartItem).where(CartItem.session_id == session_id)
	)
	return list(result.scalars().all())


async def merge_guest_cart_into_user(
	db: AsyncSession, user_id: uuid.UUID, session_id: str
) -> None:
	guest_items = await get_guest_cart_items(db, session_id)
	if not guest_items:
		return

	for guest_item in guest_items:
		user_item = await get_cart_item_by_sku(db, user_id, None, guest_item.sku_id)
		if user_item:
			user_item.quantity = max(user_item.quantity, guest_item.quantity)
			await db.delete(guest_item)
		else:
			guest_item.user_id = user_id
			guest_item.session_id = None

	await db.commit()
