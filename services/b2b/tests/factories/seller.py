import uuid

import factory

from database.models import Seller


class SellerFactory(factory.Factory):
	class Meta:
		model = Seller

	id = factory.LazyFunction(uuid.uuid4)
	email = factory.Faker("email")
	password_hash = factory.Faker("md5")
	first_name = factory.Faker("first_name")
	last_name = factory.Faker("last_name")
	middle_name = factory.Faker("first_name")

	company_name = factory.Faker("company")

	phone = factory.Faker("phone_number")
