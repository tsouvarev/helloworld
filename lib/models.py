from datetime import datetime

from pydantic import BaseModel

from .config import CITYESCAPE, MIDDLE, ORANGEKED, PIK, ZOVGOR


class BaseItem(BaseModel):
    for_json = BaseModel.dict
    vendor: str
    title: str
    start: datetime
    end: datetime
    level: int = MIDDLE
    url: str = '#'


class ItemPik(BaseItem):
    vendor: str = PIK


class ItemOrangeked(BaseItem):
    vendor: str = ORANGEKED


class ItemCityescape(BaseItem):
    vendor: str = CITYESCAPE


class ItemZovgor(BaseItem):
    vendor: str = ZOVGOR
