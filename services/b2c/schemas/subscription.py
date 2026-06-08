from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class SubscriptionEvent(str, Enum):
	BACK_IN_STOCK = "BACK_IN_STOCK"
	PRICE_DROP = "PRICE_DROP"


class SubscribeRequest(BaseModel):
	events: List[SubscriptionEvent] = Field(
		default_factory=lambda: [
			SubscriptionEvent.BACK_IN_STOCK,
			SubscriptionEvent.PRICE_DROP,
		],
	)
