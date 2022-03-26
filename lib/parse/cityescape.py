import re
from datetime import datetime
from itertools import starmap
from typing import Iterable, Iterator, List, Tuple

from funcy import cat, first
from lxml import html

from ..config import MONTHS, TODAY, Currency, Level, Vendor
from ..models import Item
from ..utils import (
    content,
    css,
    error,
    gather_chunks,
    guess_currency,
    int_or_none,
)
from . import client

MENU_ITEM = css('.menu-item.menu-item-type-post_type.menu-item-object-post a')
MONTHS_JOINED = '|'.join(MONTHS)
PRICE_RE = re.compile(r'((?=[1-9])[0-9 ]+)\s+(р\.|\$|€)')
TITLE_RE = re.compile(r'(.+?) ([1-9][0-9 -]+(?:%s).+)$' % MONTHS_JOINED)
DATE_RE = re.compile(r'([0-9]+) ?(%s)? ?([0-9]{4})?' % MONTHS_JOINED)
LEVELS_MAP = {
    'Легкий': Level.EASY,
    'Несложный': Level.EASY,
    'Средний': Level.MEDIUM,
    'Сложный': Level.HARD,
}


async def parse_cityescape() -> Iterator[Item]:
    page = await client.get('https://cityescape.ru/')
    tree = html.fromstring(page.text.encode('utf_8_sig'))
    items = ((content(x), x.attrib['href']) for x in tree.xpath(MENU_ITEM))
    return cat(await gather_chunks(5, *starmap(parse_page, items)))


async def parse_page(page_title: str, url: str) -> List[Item]:
    data = first(TITLE_RE.findall(page_title))
    if not data:
        return []

    title, dates = data

    page = await client.get(url)
    text = page.text.replace('&nbsp;', ' ')
    tree = html.fromstring(text.encode('utf_8_sig'))
    price, currency = parse_price(
        content(tree.xpath(css('#content-tab2'))[0])
    )

    items = []
    for start, end in parse_dates(dates):
        item = Item(
            vendor=Vendor.CITYESCAPE,
            start=start,
            end=end,
            title=title,
            url=url,
            price=price,
            currency=currency,
            level=first(v for k, v in LEVELS_MAP.items() if k in text),
        )
        items.append(item)
    return items


def parse_dates(
    src: str, today: datetime = TODAY
) -> Iterable[Tuple[datetime, datetime]]:
    dates = src.replace('/', ',').split(',')
    for pair in dates:
        splitted = pair.split('-')[-2:]

        if len(splitted) == 1:
            start_src, end_src = None, splitted[0]
        elif len(splitted) == 2:
            start_src, end_src = splitted
        else:
            error(f'[cityescape]: Failed to parse data "{pair}"')
            continue

        start = end = parse_date(end_src, today)
        if start_src:
            start = parse_date(start_src, start)
            if end < start:
                start = start.replace(year=start.year - 1)
        yield start, end


def parse_date(src: str, today: datetime) -> datetime:
    day, month, year = map(str.strip, DATE_RE.findall(src)[0])
    date = today.replace(
        year=int_or_none(year) or today.year,
        month=MONTHS.index(month) + 1 if month else today.month,
        # let it fail
        day=int_or_none(day) or 0,
    )
    return date


def parse_price(src: str) -> Tuple[int, Currency]:
    price = currency = None
    for x, y in PRICE_RE.findall(src):
        price = max(price or 0, int_or_none(x) or 0)
        if not currency:
            currency = y

    if not (price and currency):
        return 0, Currency.RUB

    return price, guess_currency(currency)
