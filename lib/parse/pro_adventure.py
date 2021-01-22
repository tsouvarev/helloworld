import re
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Tuple

from funcy import cat, compose, first, mapcat
from lxml import html

from ..config import MONTHS_NORM, TODAY, Level, Vendor
from ..models import Item
from ..utils import content, int_or_none
from . import client

find_dates = re.compile(r'\'?\w+', re.I | re.M).findall
find_age = compose(first, re.compile(r'\d+ лет', re.I | re.M).findall)
LEVELS_MAP: Dict[int, Level] = {
    1: Level.EASY,
    2: Level.MEDIUM,
    3: Level.HARD,
}


async def parse_pro_adventure() -> Iterator[Item]:
    all_items: List[Tuple[Item, ...]] = []
    for i in range(1, 42):
        page = await client.get(f'https://pro-adventure.ru/tours?page={i}')
        items = tuple(parse_page(page.text))
        if not items:
            # No active item found on page
            break
        all_items.append(items)
    return cat(all_items)


def parse_page(text: str) -> Iterator[Item]:
    tree = html.fromstring(text)
    for item in tree.xpath('//*[@class="catalog-item"]'):
        # tags
        item_title = item.find_class('catalog-item__title')[0]
        difficult = item.find_class('difficult')[0]
        cost = item.find_class('catalog-item__cost')[0]
        duration = item.find_class('catalog-item__time')[0]
        params = item.find_class('catalog-item__param-list')[0]

        # content
        age = int_or_none(find_age(content(params)) or '') or 18
        offset = timedelta(days=(int_or_none(content(duration)) or 1) - 1)
        date_nodes = mapcat(list, item.cssselect('div.catalog-item__dates'))

        seen = set()
        for node in date_nodes:
            value = content(node)
            if value in seen:
                continue

            seen.add(value)
            done = {int(content(x)) for x in node.cssselect('s')}
            for start in parse_dates(value):
                slots = None
                if start.day in done:
                    slots = 0

                level = int_or_none(difficult.get('class'))

                item = Item(
                    vendor=Vendor.PRO_ADVENTURE,
                    level=level and LEVELS_MAP[level],
                    start=start,
                    end=start + offset,
                    url='https://pro-adventure.ru' + item_title.get('href'),
                    title=content(item_title),
                    price=content(cost),
                    for_kids=age <= 5,
                    slots=slots,
                )

                yield item


def parse_dates(src: str, today: datetime = TODAY) -> Iterator[datetime]:
    month, *rest = find_dates(src.lower())
    if rest[0].startswith('\''):
        year = int('20' + rest[0].lstrip('\''))
        days = rest[1:]
    else:
        year = today.year
        days = rest

    for day in map(int, days):
        start = datetime(
            year=year, month=MONTHS_NORM.index(month) + 1, day=day
        )
        yield start
