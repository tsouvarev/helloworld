import re
from datetime import datetime
from functools import partial
from typing import Iterator

from funcy import first
from lxml import html

from ..config import MONTHS, MONTHS_NORM, TODAY, Vendor
from ..models import Item
from ..parse import client
from ..utils import content, css, error, mapv, warn


async def parse_teamtrip() -> Iterator[Item]:
    page = await client.get('https://team-trip.ru/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text.encode())
    for link in tree.xpath(css('.t404__link')):
        # import ipdb
        # ipdb.set_trace()
        href = link.attrib['href']
        wrapper = first(link.find_class('t404__textwrapper'))
        if not wrapper:
            warn('skip teamtrip item cause cant find wrapper')
            continue

        dates, title = wrapper.getchildren()[:2]
        if 't404__uptitle' not in dates.attrib['class']:
            warn('skip teamtrip item cause invalid state')
            continue

        for start, end in parse_dates(content(dates)):
            yield Item(
                vendor=Vendor.TEAMTRIP,
                start=start,
                end=end,
                title=content(title),
                url='https://team-trip.ru' + href,
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
