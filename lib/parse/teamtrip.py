import re
from datetime import datetime
from functools import partial
from typing import Iterator

from lxml import html

from ..config import MONTHS, TODAY, Vendor
from ..models import Item
from ..parse import client
from ..utils import error, mapv, zip_safe


async def parse_teamtrip() -> Iterator[Item]:
    page = await client.get('https://team-trip.ru/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text.encode())
    paths = (
        '//*[@class="t404__tag"]/text()',
        '//*[@class="t404__title t-heading t-heading_xs"]/text()',
        '//*[@class="t404__link"]/@href',
    )
    for dates, title, url in zip_safe(*map(tree.xpath, paths)):
        for start, end in parse_dates(dates):
            yield Item(
                vendor=Vendor.TEAMTRIP,
                start=start,
                end=end,
                title=title,
                url='https://team-trip.ru' + url,
            )


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
            yield start, end
        except Exception as e:
            error(f'[teamtrip]: Failed to parse data "{date}" ({e})')
            continue


def parse_date(src: str, today: datetime):
    data = re.split(r'\W+', src)
    if len(data) == 3:
        day, month, year = data
        return datetime(
            day=int(day), month=MONTHS.index(month) + 1, year=int(year)
        )
    elif len(data) == 2:
        day, month = data
        if not month.isdigit():
            month = MONTHS.index(month) + 1
        return today.replace(day=int(day), month=int(month))
    else:
        return today.replace(day=int(data[0]))
