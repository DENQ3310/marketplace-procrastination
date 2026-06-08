import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.catalog.base import Review


@dataclass(frozen=True, slots=True)
class ProductReviewStats:
	reviews_count: int
	rating: float


async def get_reviews_stats_by_product_ids(
	db: AsyncSession, product_ids: list[uuid.UUID]
) -> dict[uuid.UUID, ProductReviewStats]:
	if not product_ids:
		return {}

	result = await db.execute(
		select(
			Review.product_id,
			func.count(Review.id).label("reviews_count"),
			func.avg(Review.rating).label("avg_rating"),
		)
		.where(Review.product_id.in_(product_ids))
		.group_by(Review.product_id)
	)

	return {
		row.product_id: ProductReviewStats(
			reviews_count=row.reviews_count,
			rating=round(float(row.avg_rating), 1),
		)
		for row in result.all()
		if row.avg_rating is not None
	}
