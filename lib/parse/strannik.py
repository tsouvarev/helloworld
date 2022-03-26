import re
from datetime import datetime
from functools import partial
from typing import Iterator

from lxml import html

from ..config import Vendor
from ..models import Item
from ..utils import error, guess_currency, parse_int, zip_safe
from . import client

find_dates = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)').findall
clear_days = partial(re.compile(r'[0-9\s.]+[дняейь\s.]{3,}$').sub, '')


async def parse_strannik() -> Iterator[Item]:
    page = await client.get('https://strannik36.ru/grafik-pohodov')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text)
    tails = (
        '//*[@class="upcoming-hikes__item__name"]/div[1]/a/span/text()',
        '//*[@class="upcoming-hikes__item__name"]/div[1]/a/@href',
        '//*[@class="upcoming-hikes__item__dates"]/text()',
        '//*[@class="upcoming-hikes__item__price"]/span[2]/text()',
    )

    data = map(tree.xpath, tails)
    for title, href, dates, price in zip_safe(*data):
        try:
            start, end = parse_dates(dates)
        except Exception as e:
            error(f'Failed to parse "{e}"')
            continue

        yield Item(
            vendor=Vendor.STRANNIK,
            title=clear_days(title),
            url=href,
            price=parse_int(price),
            currency=guess_currency(price),
            start=start,
            end=end,
        )


def parse_dates(src: str) -> Iterator[datetime]:
    for day, month, year in find_dates(src):
        yield datetime(day=int(day), month=int(month), year=int(year))
