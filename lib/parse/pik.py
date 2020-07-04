import asyncio
import re
from datetime import datetime
from typing import Iterator

from funcy import cat, compose, first

from ..config import Level, Vendor
from ..models import Item
from . import client

PIK_URL = 'https://turclub-pik.ru/search_ajax/trips/'
MONTHS = 'янв фев мар апр мая июн июл авг сен окт ноя дек'.split()
LEVELS = {
    'very_easy': Level.VERY_EASY,
    'easy': Level.EASY,
    'middle': Level.MEDIUM,
    'hard': Level.HARD,
    'very_hard': Level.VERY_HARD,
}
parse_dates = compose(
    first, re.compile(r'^с (\d+) ?(\w{3})? ?по (\d+) (\w{3}) (\d{4})').findall
)


async def get_page(page) -> dict:
    resp = await client.get(PIK_URL, params={'page': page}, verify=False)
    return resp.json()


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


def parse_date(src: str):
    start_day, start_month, end_day, end_month, end_year = parse_dates(src)
    start_month = start_month or end_month
    start_month = MONTHS.index(start_month) + 1
    end_month = MONTHS.index(end_month) + 1

    start_year = end_year = int(end_year)
    if start_month > end_month:
        start_year -= 1

    yield datetime(start_year, start_month, int(start_day))
    yield datetime(end_year, end_month, int(end_day))


def parse_item(item: dict) -> Item:
    start, end = parse_date(item['duration_explained'])
    slots = None
    if item['is_full']:
        slots = 0
    return Item(
        vendor=Vendor.PIK,
        start=start,
        end=end,
        title=item['name'],
        price=item['costs_rubs'],
        url='https://turclub-pik.ru' + item['absolute_url'],
        level=LEVELS[item['track']['difficulty']['slug']],
        length=item['track']['length'],
        slots=slots,
    )
