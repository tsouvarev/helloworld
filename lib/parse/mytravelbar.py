from datetime import datetime
from typing import Tuple

import httpx
from cssselect import GenericTranslator
from funcy import first, keep
from lxml import html

from ..config import MYTRAVELBAR, TODAY, Level
from ..models import Item
from ..utils import format_price, int_or_none, zip_safe

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)


async def parse_mytravelbar():
    page = await httpx.get('https://mytravelbar.ru/')
    return parse_page(page.text)


def parse_page(text):
    css = GenericTranslator().css_to_xpath
    tree = html.fromstring(text)

    paths = (
        'div.js-product-name',
        'div.js-product-name + div > *:first-child',
        'div.js-product-name + div > ul > li:nth-child(1)',
        'div.js-product-name + div > ul > li:nth-child(2)',
        'div.js-product-name + div > ul > li:nth-child(2) > strong',
    )

    parsed = (keep(str.strip, tree.xpath(css(x) + '/text()')) for x in paths)

    hrefs = keep(str.strip, tree.xpath(css('a.js-product-link') + '/@href'))

    for date, title, length, slot, price, href in zip_safe(*parsed, hrefs):
        start, end = parse_date(TODAY, date)
        yield Item(
            vendor=MYTRAVELBAR,
            start=start,
            end=end,
            title=title,
            url=href,
            level=Level.EASY,
            length=int_or_none(length),
            price=format_price(price),
            slots=int_or_none(first(slot.split())) or 0,
        )


def parse_date(now: datetime, src: str) -> Tuple[datetime, datetime]:
    data = src.lower().split()
    if len(data) == 3:
        day, month, _ = data
        date = format_date(now, day, month)
        return date, date
    else:
        day0, _, day1, month, _ = src.lower().split()
        return format_date(now, day0, month), format_date(now, day1, month)


def format_date(now, day, month) -> datetime:
    return now.replace(day=int(day), month=MONTHS.index(month) + 1)
