from datetime import datetime

from pydantic import BaseModel

from .config import MIDDLE


class Item(BaseModel):
    for_json = BaseModel.dict
    vendor: str
    title: str
    start: datetime
    end: datetime
    level: int = MIDDLE
    url: str = '#'
