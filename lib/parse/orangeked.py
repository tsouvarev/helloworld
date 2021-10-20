import re
from datetime import datetime
from typing import Iterator

from funcy import compose, first, nth
from lxml import html

from ..config import MONTHS, TODAY, Level, Vendor
from ..models import Item
from ..utils import css, gather_chunks, silent
from . import client

find_dates = compose(
    first,
    re.compile(r'([0-9]+) (\w*)[^0-9]+([0-9]+) (\w+)').findall,
)


async def parse_orangeked() -> Iterator[Item]:
    listing = await client.get('http://orangeked.ru/tours')
    tree = html.fromstring(listing.text.encode())
    links = set(tree.xpath(css('#tourList a.item-link') + '/@href'))
    return iter(await gather_chunks(5, *map(parse_page, links)))


@silent
async def parse_page(path: str) -> Item:
    url = 'http://orangeked.ru' + path
    page = await client.get(url)
    tree = html.fromstring(page.text.encode())
    level = len(tree.xpath('//*[@class="icons-difficulty"]/i[@class="i"]'))
    slots = len(tree.xpath('//*[@class="icons-groupsize"]/i'))
    slots_taken = len(
        tree.xpath('//*[@class="icons-groupsize"]/i[@class="i"]')
    )
    title = tree.xpath('//*[@id="k2Container"]/header/h1/text()')[0]
    start, end = parse_dates(
        tree.xpath('//*[@class="tour__short-info__item__value"]/text()')[1]
    )
    price = nth(
        2, tree.xpath('//*[@class="tour__short-info__item__value"]/text()')
    )
    item = Item(
        vendor=Vendor.ORANGEKED,
        level=Level.index(level - 1),
        start=start,
        end=end,
        url=url,
        title=title,
        price=price,
        slots=slots - slots_taken,
    )
    return item


def parse_dates(src: str, today: datetime = TODAY):
    start_day, start_month, end_day, end_month = find_dates(src)
    start_month = start_month or end_month
    start_month = MONTHS.index(start_month) + 1
    end_month = MONTHS.index(end_month) + 1

    start_year = end_year = today.year
    if end_month < today.month:
        # Goes to the next year
        start_year += 1
        end_year += 1

    yield datetime(start_year, start_month, int(start_day))
    yield datetime(end_year, end_month, int(end_day))
