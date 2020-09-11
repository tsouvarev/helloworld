import re
from datetime import datetime
from typing import Iterator, Tuple

from funcy import first, post_processing

from ..config import MONTHS, TODAY, Vendor
from ..models import Item
from ..utils import json_loads, error
from . import client

DATE_RE = re.compile(r'([0-9]+)\s*([а-я]+)')
ITEMS_RE = re.compile(r'var rendererModel = ({.+?});', re.M)
ITEMS_DATA_RE = re.compile(r'warmupData\s*=\s*({.+?});', re.M)


def parse_items(src: str) -> dict:
    js = json_loads(ITEMS_RE.findall(src)[0])['pageList']['pages']
    return {i['pageId']: i['pageUriSEO'] for i in js}


@post_processing(dict)
def parse_data(src: str):
    js = json_loads(ITEMS_DATA_RE.findall(src)[0])
    data = js['wixappsCoreWarmup']['appbuilder']['items']
    for item in first(data.values()).values():
        if not item['links']['title']:
            # Индивидуальный поход, забронировано
            continue

        id_ = item['links']['title']['pageId'].lstrip('#')
        info = {
            'date': item['i6m28pva'],
            'price': item['Strng_sTxt2-equ'],
            'title': item['title'],
        }
        yield id_, info


async def parse_pohodtut() -> Iterator[Item]:
    page = await client.get('https://www.pohodtut.ru')
    return parse_page(page.text)


def parse_page(text):
    items = parse_items(text)
    items_data = parse_data(text)
    for key, url in items.items():
        if key not in items_data:
            # Поход недоступен
            continue

        data = items_data[key]
        try:
            start, end = parse_date(data['date'])
        except Exception as e:
            error(repr((e, data)))
            continue

        while start > end:
            # fix typo
            start = start.replace(month=start.month - 1)

        yield Item(
            vendor=Vendor.POHODTUT,
            start=start,
            end=end,
            title=data['title'],
            price=data['price'],
            url='https://www.pohodtut.ru/' + url,
        )


def parse_date(src: str, today=TODAY) -> Iterator[Tuple[datetime, datetime]]:
    dates = DATE_RE.findall(src)
    if len(dates) == 1:
        dates.extend(dates)

    for day, month in dates:
        yield today.replace(day=int(day), month=MONTHS.index(month) + 1)
