import re
from datetime import datetime
from typing import Iterator

from lxml import html

from ..config import Level, Vendor
from ..models import Item
from ..utils import content, zip_safe
from . import client

MONTHS = 'янв фев мар апр ма июн июл авг сен окт ноя дек'.split()

find_dates = re.compile(
    r'([0-9]+)\s(%s)\w*\s([0-9]+)' % '|'.join(MONTHS)
).findall


async def parse_perehod() -> Iterator[Item]:
    page = await client.get(
        'https://club-perexod.ru/ajax/filter_shedule.php?r=0&t=&d=&c=&all=1'
    )
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text)
    tails = (
        '//*[@class="b-schedule-table__name"]/a/text()',
        '//*[@class="b-schedule-table__name"]/a/@href',
        '//*[@class="b-schedule-table__date"][descendant-or-self::text()]',
        '//*[@class="b-schedule-table__price-young"]/text()',
        '//*[@class="b-schedule-table__complexity"]',
    )

    data = map(tree.xpath, tails)
    for title, href, dates, price, complexity in zip_safe(*data):
        start, end = parse_dates(content(dates))
        level = len(complexity.xpath('div[contains(@class, "b-active")]')) - 1
        yield Item(
            vendor=Vendor.PEREHOD,
            title=title,
            url='https://club-perexod.ru' + href,
            price=price,
            start=start,
            end=end,
            level=Level.index(level),
        )


def parse_dates(src: str) -> Iterator[datetime]:
    for day, month, year in find_dates(src):
        yield datetime(
            day=int(day), month=MONTHS.index(month) + 1, year=int(year)
        )
