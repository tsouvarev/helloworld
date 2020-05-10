from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .config import DEFAULT_LEVEL


class Item(BaseModel):
    for_json = BaseModel.dict
    vendor: str
    title: str
    start: datetime
    end: datetime
    level: int = DEFAULT_LEVEL
    url: str = '#'
    price: Optional[str] = None
    length: Optional[int] = None
    slots: Optional[int] = None

    class Config:
        extra = 'forbid'
