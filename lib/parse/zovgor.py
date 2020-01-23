from datetime import datetime
from itertools import zip_longest

import httpx
from funcy import chain, partial, collecting
from lxml import html

from ..config import EASY, HARD, MIDDLE, ZOVGOR
from ..models import Item
from ..utils import mapv

LEVELS = {
    'низкая': EASY,
    'средняя': MIDDLE,
    'высокая': HARD,
}


async def parse_zovgor():
    page = await httpx.get('https://zovgor.com/shedule.html')
    return parse_page(page.text)


def parse_page(text):
    parse_dt = partial(parse_date, datetime.now().year)
    tree = html.fromstring(text.encode())
    path = f'//*[@id="main"]/table/tbody/tr[position()>1]/'
    data = zip_longest(
        tree.xpath(path + 'td[1]/a[1]/text()'),
        tree.xpath(path + 'td[1]/a[2]/text()'),
        tree.xpath(path + 'td[1]/a[1]/@href'),
        tree.xpath(path + 'td[2]/text()'),
        tree.xpath(path + 'td[4]/text()'),
        fillvalue='',
    )

    for title, title2, url, date, level in data:
        start, end = map(parse_dt, date.split('-', 1))
        yield Item(
            vendor=ZOVGOR,
            title=title + title2,
            url='https://zovgor.com/' + url,
            level=LEVELS[level],
            start=start,
            end=end,
        )


def parse_date(now_year: int, src: str) -> datetime:
    date = mapv(int, src.split('.'))
    if len(date) == 2:
        (day, month), year = date, now_year
    else:
        day, month, year = date
        year = 2000 + year
    return datetime(year=year, month=month, day=day)
