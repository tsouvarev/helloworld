import asyncio
from datetime import datetime, timedelta
from typing import Iterator, Tuple

from funcy import cat

from ..config import Level, Vendor
from ..models import Item
from . import client

PIK_URL = 'https://turclub-pik.ru/api/v1/public/search/'
LEVELS = {
    'very_easy': Level.VERY_EASY,
    'easy': Level.EASY,
    'middle': Level.MEDIUM,
    'hard': Level.HARD,
    'very_hard': Level.VERY_HARD,
}


async def get_page(page) -> dict:
    resp = await client.get(PIK_URL, params={'page': page})
    return resp.json()['trips']


async def parse_pik(batch=10) -> Iterator[Item]:
    items = {}
    start = 1
    while True:
        coros = map(get_page, range(start, start + batch))
        done = False

        for item in cat(await asyncio.gather(*coros)):
            done = done or item['id'] in items
            items[item['id']] = item

        if done:
            return map(parse_item, items.values())
        start += batch


def parse_date(src: str, duration: int) -> Tuple[datetime, datetime]:
    year, month, day = map(int, src.split('-'))
    start = datetime(year, month, day)
    return start, start + timedelta(days=duration)


def parse_item(item: dict) -> Item:
    route = item['route']
    start, end = parse_date(item['start'], route['duration'])
    slots = None
    if item['is_full']:
        slots = 0

    if item['has_discount']:
        price = item['discount_cost_string']
    else:
        price = item['cost_string']

    return Item(
        vendor=Vendor.PIK,
        start=start,
        end=end,
        title=route['name'],
        price=price,
        url='https://turclub-pik.ru/pohod/{slug}/'.format_map(route),
        level=LEVELS[route['difficulty']['slug']],
        length=route['path_length'],
        slots=slots,
    )
