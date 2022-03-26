from datetime import datetime
from typing import Iterator

from lxml import html

from ..config import MONTHS, TODAY, Vendor
from ..models import Item
from ..utils import content, guess_currency, int_or_none, parse_int, zip_safe
from . import client


async def parse_napravlenie() -> Iterator[Item]:
    page = await client.get('https://www.napravlenie.info/kalendar/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text)
    prefix = '//div[not(contains(@class, "oldTours"))]/*[@class="aItem"]'
    dates = tree.xpath(
        f'{prefix}//*[@class="abody"]/*[@class="blueTextBg"]/text()'
    )
    price_nodes = tree.xpath(
        f'{prefix}//*[@class="afoot"]/span[1]/*[@class="textIco price"]'
    )
    prices = map(content, price_nodes)
    slots = tree.xpath(
        f'{prefix}//*[@class="afoot"]/span[3]/*[@class="textIco"]/text()'
    )
    titles = tree.xpath(f'{prefix}//*[@class="abody"]/h2/a/text()')
    hrefs = tree.xpath(f'{prefix}//*[@class="abody"]/h2/a/@href')
    for date, price_src, slot, title, href in zip_safe(
        dates, prices, slots, titles, hrefs
    ):
        start, end = parse_dates(TODAY, date)
        yield Item(
            vendor=Vendor.NAPRAVLENIE,
            start=start,
            end=end,
            title=title.replace(' / 2020', ''),
            url='https://www.napravlenie.info' + href,
            # Comma separates children price,
            # Currency is somewhere
            price=parse_int(price_src.split(',', 1)[0]),
            currency=guess_currency(price_src),
            slots=int_or_none(slot) or 0,
        )


def parse_dates(now: datetime, src: str):
    start_, end_ = map(str.strip, src.split('-'))
    end = parse_date(now, end_)
    start = parse_date(end, start_)
    return start, end


def parse_date(now: datetime, src: str) -> datetime:
    data = src.split()
    if len(data) == 3:
        day, month, year = data
        return datetime(
            day=int(day), month=MONTHS.index(month) + 1, year=int(year)
        )
    elif len(data) == 2:
        day, month = data
        return now.replace(day=int(day), month=MONTHS.index(month) + 1)
    else:
        return now.replace(day=int(data[0]))
