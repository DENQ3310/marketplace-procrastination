from database.models.identity.user import User, Seller
import factory
import uuid
from datetime import datetime


class UserFactory(factory.Factory):
	class Meta:
		model = User

	id = factory.LazyFunction(uuid.uuid4)
	username = factory.Sequence(lambda n: f"user_{n}")
	email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
	password_hash = factory.Faker("password")
	created_at = factory.LazyFunction(datetime.now)


class SellerFactory(factory.Factory):
	class Meta:
		model = Seller

	id = factory.LazyFunction(uuid.uuid4)
	email = factory.Sequence(lambda n: f"seller_{n}@example.com")
	password_hash = factory.Sequence(lambda n: f"seller_hash_{n}")
	first_name = factory.Faker("first_name")
	last_name = factory.Faker("last_name")
	middle_name = ""
	company_name = factory.Sequence(lambda n: f"Seller Company {n}")
	phone = factory.Sequence(lambda n: f"+7900000{n:04d}")
	created_at = factory.LazyFunction(datetime.now)
	updated_at = factory.LazyFunction(datetime.now)
