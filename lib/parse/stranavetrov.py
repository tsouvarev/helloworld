import re
from datetime import datetime
from typing import Any, Dict, Optional

from funcy import chunks, first
from lxml import html

from ..config import Level, Vendor
from ..models import Item
from ..utils import content, guess_currency, int_or_none, parse_int
from . import client

find_dates = re.compile(r'\d{,2}\.\d{,2}\.\d{4}', re.I | re.M).findall
LEVELS_MAP: Dict[str, Level] = {
    'легкий': Level.EASY,
    'средний': Level.MEDIUM,
    'сложный': Level.HARD,
}


def classer(item):
    def inner(name: str, default: Optional[Any] = '') -> Any:
        node = first(item.find_class(name))
        if node is not None:
            return content(node)
        return default

    return inner


async def parse_stranavetrov():
    resp = await client.post(
        'https://stranavetrov.ru/all-travel', params={'limit': 999}
    )
    return tuple(parse_page(resp.content.decode('utf8', errors='ignore')))


def parse_page(text):
    tree = html.fromstring(text)
    for item in tree.xpath('//*[@itemtype="https://schema.org/Product"]'):
        cls = classer(item)
        link = item.cssselect('.eventlink a')[0].get('href')
        price = cls('eventnewprice') or cls('eventprice', '')
        dates = chunks(2, map(parse_date, find_dates(cls('dataevent'))))
        for start, end in dates:
            yield Item(
                start=start,
                end=end,
                vendor=Vendor.STRANAVETROV,
                level=LEVELS_MAP[cls('stangeevent').lower()],
                url='https://stranavetrov.ru' + link,
                title=cls('eventname'),
                length=int_or_none(cls('kmevent')),
                price=parse_int(price),
                currency=guess_currency(price),
            )


def parse_date(src: str) -> datetime:
    day, month, year = map(int, src.split('.'))
    return datetime(day=day, month=month, year=year)
