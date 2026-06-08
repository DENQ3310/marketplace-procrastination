import factory
import uuid
from datetime import datetime
from database.models import CartItem
from database.models.personal.profile import Favorite, Subscription
from database.models.storefront.main import (
	Banner,
	Collection,
	CollectionProduct,
)


class FavoriteFactory(factory.Factory):
	class Meta:
		model = Favorite

	user_id = factory.LazyFunction(uuid.uuid4)
	product_id = factory.LazyFunction(uuid.uuid4)
	added_at = factory.LazyFunction(datetime.now)


class SubscriptionFactory(factory.Factory):
	class Meta:
		model = Subscription

	user_id = factory.LazyFunction(uuid.uuid4)
	product_id = factory.LazyFunction(uuid.uuid4)
	notify_in_stock = factory.LazyFunction(bool)
	notify_price_down = factory.LazyFunction(bool)
	created_at = factory.LazyFunction(datetime.now)


class CollectionFactory(factory.Factory):
	class Meta:
		model = Collection

	id = factory.LazyFunction(uuid.uuid4)
	title = factory.Faker("sentence")
	description = factory.Faker("text")
	cover_image_url = factory.Faker("image_url")
	target_url = factory.Faker("url")
	priority = factory.Faker("pyint", min_value=0, max_value=100)
	start_date = factory.LazyFunction(datetime.now)
	is_active = True
	created_at = factory.LazyFunction(datetime.now)


class CollectionProductFactory(factory.Factory):
	class Meta:
		model = CollectionProduct

	product_id = factory.LazyFunction(uuid.uuid4)
	collection_id = factory.LazyFunction(uuid.uuid4)


class CartItemFactory(factory.Factory):
	class Meta:
		model = CartItem

	id = factory.LazyFunction(uuid.uuid4)
	user_id = factory.LazyFunction(uuid.uuid4)
	session_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
	sku_id = factory.LazyFunction(uuid.uuid4)
	quantity = factory.Faker("pyint", min_value=100, max_value=1000)
	created_at = factory.LazyFunction(datetime.now)
	updated_at = factory.LazyFunction(datetime.now)


class BannerFactory(factory.Factory):
	class Meta:
		model = Banner

	id = factory.LazyFunction(uuid.uuid4)
	title = factory.Faker("sentence")
	image_url = factory.Faker("image_url")
	link = factory.Faker("url")
	priority = factory.Faker("pyint", min_value=0, max_value=100)
	is_active = True
	start_at = factory.LazyFunction(datetime.now)
	end_at = factory.LazyFunction(datetime.now)
	created_at = factory.LazyFunction(datetime.now)
