from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


class Banner(BaseModel):
	id: uuid.UUID
	title: str
	image_url: str
	link: str
	ordering: int
	active_from: datetime | None = None
	active_to: datetime | None = None


class BannerEventItem(BaseModel):
	banner_id: uuid.UUID
	event: Literal["impression", "click"]
	timestamp: datetime


class BannerEventsRequest(BaseModel):
	events: list[BannerEventItem] = Field(min_length=1)
