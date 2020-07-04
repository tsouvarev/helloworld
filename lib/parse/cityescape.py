import re
from datetime import datetime
from typing import Iterable, Iterator, Optional, Tuple

from cssselect import GenericTranslator
from funcy import cat, first
from lxml import html

from ..config import TODAY, Level, Vendor
from ..models import Item
from ..utils import gather_chunks, int_or_none
from . import client

cssx = GenericTranslator().css_to_xpath

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)
MONTHS_JOINED = '|'.join(MONTHS)
PRICE_RE = re.compile(r'((?=[1-9])[0-9 ]+)\s+(р\.|\$|€)')
TITLE_RE = re.compile(r'(.+?) ([1-9][0-9 -]+(?:%s).+)$' % MONTHS_JOINED)
DATE_RE = re.compile(r'([0-9]+) ?(%s)? ?([0-9]{4})?' % MONTHS_JOINED)
LEVELS_MAP = {
    '>Легкий': Level.EASY,
    '>Несложный': Level.EASY,
    '>Средний': Level.MEDIUM,
    '>Сложный': Level.HARD,
}


async def parse_cityescape() -> Iterator[Item]:
    page = await client.get('https://cityescape.ru/')
    tree = html.fromstring(page.text.encode())

    items = cat(
        x.xpath('a/@href')
        for x in tree.xpath(cssx('.menu-item-object-post'))
        if 'Ожидается' not in x.text_content()
    )

    return cat(await gather_chunks(5, *map(parse_page, items)))


async def parse_page(url: str):
    page = await client.get(url)
    text = page.text.replace('&nbsp;', ' ')
    items = []
    tree = html.fromstring(text.encode())
    price = parse_price(
        ''.join(tree.xpath('//*[@id="content-tab2"]')[0].itertext())
    )

    level = None
    for k, v in LEVELS_MAP.items():
        if k in text:
            level = v
            break

    for page_title in tree.xpath('//*[@class="page__title"]/text()'):
        data = first(TITLE_RE.findall(page_title))
        if not data:
            # fixme: warn
            continue

        title, dates = data
        for start, end in parse_dates(dates):
            item = Item(
                vendor=Vendor.CITYESCAPE,
                start=start,
                end=end,
                title=title,
                url=url,
                price=price and '{} {}'.format(*price),
                level=level,
            )
            items.append(item)
    return items


def parse_dates(src: str) -> Iterable[Tuple[datetime, datetime]]:
    dates = src.split(',')
    for pair in dates:
        splitted = pair.split('-')

        if len(splitted) == 1:
            start_src, end_src = None, splitted[0]
        else:
            start_src, end_src = splitted

        start = end = parse_date(end_src, TODAY)
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


def parse_price(src: str) -> Optional[Tuple[int, int]]:
    price = currency = None
    for x, y in PRICE_RE.findall(src):
        price = max(price or 0, int_or_none(x))
        if not currency:
            currency = y

    if not price or not currency:
        return None

    return price, currency
