from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from .config import Currency, Level, Vendor
from .utils import hash_uid, utcnow


class Item(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = 'forbid'

    url: str
    vendor: Vendor
    title: str
    start: datetime
    end: datetime
    for_kids: bool = False
    level: Optional[Level] = None
    price: int = 0
    currency: Currency = Currency.RUB
    length: Optional[int] = None
    slots: Optional[int] = None
    id: Optional[str] = None
    created: datetime = Field(default_factory=utcnow)

    @validator('id', pre=True, always=True)
    def default_id(cls, v, *, values):
        return v or hash_uid('{url}:{start}:{end}'.format_map(values))

    def for_json(self):
        return self.dict()
