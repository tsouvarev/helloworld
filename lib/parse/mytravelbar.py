from datetime import datetime

import httpx
from cssselect import GenericTranslator
from funcy import first, keep
from lxml import html

from ..config import MYTRAVELBAR, TODAY
from ..models import Item
from ..utils import int_or_none, zip_safe
from ..utils.text import format_price

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
        'div.js-product-name + div > strong',
        'div.js-product-name + div > ul > li:nth-child(1)',
        'div.js-product-name + div > ul > li:nth-child(2)',
        'div.js-product-name + div > ul > li:nth-child(2) > strong',
    )

    parsed = (keep(str.strip, tree.xpath(css(x) + '/text()')) for x in paths)

    hrefs = keep(str.strip, tree.xpath(css('a.js-product-link') + '/@href'))

    for date, title, length, slot, price, href in zip_safe(*parsed, hrefs):
        start = parse_date(TODAY, date)
        yield Item(
            vendor=MYTRAVELBAR,
            start=start,
            end=start,
            title=title,
            url=href,
            price=format_price(price),
            slots=int_or_none(first(slot.split())) or 0,
        )


def parse_date(now: datetime, src: str) -> datetime:
    day, month, _ = src.lower().split()
    # fixme: year
    return now.replace(day=int(day), month=MONTHS.index(month) + 1)
