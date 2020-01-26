import re
from datetime import datetime

import httpx
from funcy import compose, first
from lxml import html

from ..config import LEVELS, ORANGEKED
from ..models import Item
from ..utils import gather_chunks, silent

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)
parse_dates = compose(
    first, re.compile(r'([0-9]+) (\w*) ?- ([0-9]+) (\w+)').findall,
)


async def parse_orangeked():
    listing = await httpx.get('http://orangeked.ru/tours')
    tree = html.fromstring(listing.text.encode())
    links = set(tree.xpath('//*[@id="tourList"]/div/div/div/a/@href'))
    return await gather_chunks(5, *map(parse_page, links))


@silent
async def parse_page(path: str) -> Item:
    url = 'http://orangeked.ru' + path
    page = await httpx.get(url)
    tree = html.fromstring(page.text.encode())
    level = len(tree.xpath('//*[@class="icons-difficulty"]/i[@class="i"]'))
    title = tree.xpath('//*[@id="k2Container"]/header/h1/text()')[0]
    start, end = parse_date(
        tree.xpath('//*[@class="tour__short-info__item__value"]/text()')[1]
    )
    return Item(
        vendor=ORANGEKED,
        level=LEVELS[level - 1],
        start=start,
        end=end,
        url=url,
        title=title,
    )


def parse_date(src: str):
    start_day, start_month, end_day, end_month = parse_dates(src)
    start_month = start_month or end_month
    start_month = MONTHS.index(start_month) + 1
    end_month = MONTHS.index(end_month) + 1

    now = datetime.now()
    start_year = end_year = now.year

    if end_month < now.month < start_month:
        end_year += 1

    yield datetime(start_year, start_month, int(start_day))
    yield datetime(end_year, end_month, int(end_day))
