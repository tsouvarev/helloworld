from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from .config import Level, Vendor
from .utils import hash_uid


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
    price: Optional[str] = None
    length: Optional[int] = None
    slots: Optional[int] = None
    id: Optional[str] = None

    @validator('id', pre=True, always=True)
    def default_id(cls, v, *, values):
        return v or hash_uid(values['url'])

    def for_json(self):
        return self.dict()
