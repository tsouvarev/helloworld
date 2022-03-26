import re
from datetime import datetime
from functools import partial
from itertools import starmap
from typing import Iterator, List

from funcy import cat, first
from lxml import html

from ..config import MONTHS, MONTHS_NORM, TODAY, Vendor
from ..models import Item
from ..parse import client
from ..utils import (
    content,
    css,
    error,
    gather_chunks,
    guess_currency,
    mapv,
    parse_int,
    warn,
    zip_safe,
)


async def parse_teamtrip() -> Iterator[Item]:
    page = await client.get('https://team-trip.ru/')
    tree = html.fromstring(page.text.encode())
    items = []
    links = tree.xpath(css('.t404__link'))
    dates = tree.xpath(css('.t404__tag'))
    for link, date in zip_safe(links, dates):
        href = link.attrib['href']
        wrapper = first(link.find_class('t404__textwrapper'))
        if wrapper is None:
            warn('skip teamtrip item cause cant find wrapper')
            continue
        items.append(('https://team-trip.ru' + href, content(date)))
    return cat(await gather_chunks(5, *starmap(parse_page, items)))


async def parse_page(url: str, date: str) -> List[Item]:
    page = await client.get(url)
    tree = html.fromstring(page.text.encode())
    title = content(tree.xpath(css('.t-cover .t-title'))[0])
    *_, price = map(content, tree.xpath(css('.t498 .t-name_xl')))

    items = []
    for start, end in parse_dates(date):
        items.append(
            Item(
                vendor=Vendor.TEAMTRIP,
                start=start,
                end=end,
                title=title,
                price=parse_int(price),
                currency=guess_currency(price),
                url=url,
            )
        )
    return items


re_by_year = partial(
    # 2020 01 -- missing slash
    re.compile(r'([0-9]{4})\s+([0-9]{2})').sub,
    r'\1/\2',
)

re_by_comma = partial(
    # comma instead of slash
    re.compile(r',\s*([0-9]{1,2}[\s-])').sub,
    r'/\1',
)


def split_dates(src: str):
    return mapv(str.strip, re_by_year(re_by_comma(src)).split('/'))


def parse_dates(src: str, today: datetime = TODAY):
    for date in split_dates(src):
        try:
            start_, end_ = map(str.strip, re.split(r'[–\-—]', date))
            end = parse_date(end_, today)
            start = parse_date(start_, end)
            if start > end:
                start = start.replace(year=start.year - 1)
            yield start, end
        except Exception as e:
            error(f'[teamtrip]: Failed to parse data "{date}" ({e})')
            continue


def parse_date(src: str, today: datetime):
    data = re.split(r'\W+', src)
    if len(data) == 3:
        day, month, year = data
        return datetime(day=int(day), month=month_int(month), year=int(year))
    elif len(data) == 2:
        day, month = data
        return today.replace(day=int(day), month=month_int(month))
    else:
        return today.replace(day=int(data[0]))


def month_int(value: str) -> int:
    if value.isdigit():
        return int(value)

    val = value.lower()
    try:
        return MONTHS.index(val) + 1
    except ValueError:
        return MONTHS_NORM.index(val) + 1
