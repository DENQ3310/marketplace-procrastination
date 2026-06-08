import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PaymentMethodResponse(BaseModel):
	type: Literal["CARD", "SBP", "WALLET"]
	card_last4: str | None = Field(default=None, pattern="^[0-9]{4}$")
	card_brand: Literal["VISA", "MASTERCARD", "MIR"] | None = None
	is_default: bool = False

	id: uuid.UUID
	created_at: datetime
