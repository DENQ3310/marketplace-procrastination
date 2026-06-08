from random import random
import factory
import uuid
from datetime import datetime
from database.models.orders.order import Order, OrderStatusEnum, OrderStatusHistory
from database.models.orders.order_item import OrderItem
from database.models.personal.address import Address
from database.models.personal.payment_method import PaymentMethod, PaymentMethodTypeEnum
import hashlib


class AddressFactory(factory.Factory):
	class Meta:
		model = Address

	id = factory.LazyFunction(uuid.uuid4)
	country = factory.Sequence(lambda n: f"Country {n}")
	region = factory.Sequence(lambda n: f"Region {n}")
	city = factory.Sequence(lambda n: f"City {n}")
	street = factory.Sequence(lambda n: f"Street {n}")
	building = factory.Sequence(lambda n: f"Building {n}")
	apartment = factory.Sequence(lambda n: f"Apartment {n}")
	postal_code = factory.Sequence(lambda n: f"Postal Code {n}")
	recipient_name = factory.Sequence(lambda n: f"Recipient Name {n}")
	recipient_phone = factory.Sequence(lambda n: f"+7900000{n:04d}")
	is_default = False
	comment = factory.Sequence(lambda n: f"Comment {n}")
	created_at = factory.LazyFunction(datetime.now)
	user_id = factory.LazyFunction(uuid.uuid4)


class PaymentMethodFactory(factory.Factory):
	class Meta:
		model = PaymentMethod

	id = factory.LazyFunction(uuid.uuid4)
	type = PaymentMethodTypeEnum.CARD
	card_last4 = factory.LazyFunction(lambda: "1234")
	card_brand = "VISA"
	is_default = False
	created_at = factory.LazyFunction(datetime.now)
	user_id = factory.LazyFunction(uuid.uuid4)


class OrderFactory(factory.Factory):
	class Meta:
		model = Order

	id = factory.LazyFunction(uuid.uuid4)
	buyer_id = factory.LazyFunction(uuid.uuid4)
	status = OrderStatusEnum.PAID
	number = factory.LazyFunction(lambda: str(uuid.uuid4()))
	subtotal = factory.Faker("pyint", min_value=1000, max_value=10000)
	delivery_cost = factory.Faker("pyint", min_value=100, max_value=1000)
	total = factory.LazyAttribute(lambda obj: obj.subtotal + obj.delivery_cost)
	address_id = factory.SubFactory(AddressFactory)
	payment_method_id = factory.SubFactory(PaymentMethodFactory)
	comment = factory.LazyFunction(lambda: f"Order {uuid.uuid4().hex[:8]}")
	idempotency_key = factory.LazyFunction(uuid.uuid4)
	idempotency_request_hash = factory.LazyFunction(
		lambda: hashlib.sha256(f"{uuid.uuid4().hex[:8]}".encode()).hexdigest()
	)


class OrderItemFactory(factory.Factory):
	class Meta:
		model = OrderItem

	id = factory.LazyFunction(uuid.uuid4)
	order_id = factory.SubFactory(OrderFactory)
	sku_id = factory.LazyFunction(uuid.uuid4)
	product_id = factory.LazyFunction(uuid.uuid4)
	product_title = factory.LazyFunction(lambda: f"Product {str(uuid.uuid4())}")
	sku_name = factory.LazyFunction(lambda: f"SKU {str(uuid.uuid4())}")
	quantity = factory.Faker("pyint", min_value=1, max_value=10)
	unit_price = factory.Faker("pyint", min_value=100, max_value=10_000)
	line_total = factory.LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
	image_url = factory.LazyFunction(
		lambda: f"https://example.com/image-{uuid.uuid4().hex[:8]}.jpg"
	)


class OrderStatusHistoryFactory(factory.Factory):
	class Meta:
		model = OrderStatusHistory

	id = factory.LazyFunction(uuid.uuid4)
	order_id = factory.SubFactory(OrderFactory)
	status = factory.LazyFunction(lambda: random.choice(OrderStatusEnum))
	changed_at = factory.LazyFunction(datetime.now)
	reason = factory.LazyFunction(lambda: f"Reason {uuid.uuid4().hex[:8]}")
