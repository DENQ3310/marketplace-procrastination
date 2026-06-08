import uuid

import factory

from database.models.catalog.base import (
	Category,
	Product,
	ProductStatusEnum,
)
from database.models.catalog.variants import Sku


class CategoryFactory(factory.Factory):
	class Meta:
		model = Category

	id = factory.LazyFunction(uuid.uuid4)
	parent_id = None
	name = factory.Faker("sentence", nb_words=2)
	slug = factory.Faker("slug")
	description = None
	is_active = True


class ProductFactory(factory.Factory):
	class Meta:
		model = Product

	id = factory.LazyFunction(uuid.uuid4)
	seller_id = factory.LazyFunction(uuid.uuid4)
	category_id = factory.LazyFunction(uuid.uuid4)
	title = factory.Faker("sentence", nb_words=3)
	slug = factory.Faker("slug")
	description = factory.Faker("sentence", nb_words=6)
	status = ProductStatusEnum.MODERATED
	deleted = False
	moderator_comment = ""
	blocking_reason_title = None
	field_reports = factory.LazyFunction(list)


class SkuFactory(factory.Factory):
	class Meta:
		model = Sku

	id = factory.LazyFunction(uuid.uuid4)
	product_id = factory.LazyFunction(uuid.uuid4)
	name = factory.Faker("sentence", nb_words=2)
	price = factory.Faker("pyint", min_value=100, max_value=10000)
	discount = 0
	cost_price = 0
	stock_quantity = 0
	active_quantity = factory.Faker("pyint", min_value=0, max_value=100)
	reserved_quantity = 0
	article = ""
