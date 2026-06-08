from sqlalchemy import select

from database.models import Seller

from sqlalchemy.ext.asyncio import AsyncSession


async def add_seller(seller: Seller, db: AsyncSession) -> Seller:
	db.add(seller)
	await db.commit()
	await db.refresh(seller)
	return seller


async def get_seller_by_email(email: str, db: AsyncSession) -> Seller | None:
	result = await db.execute(select(Seller).where(Seller.email == email))
	seller = result.scalar_one_or_none()

	return seller
