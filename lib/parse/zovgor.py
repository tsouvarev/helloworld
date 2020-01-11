from datetime import datetime

import httpx
from funcy import chain, lmap, partial
from lxml import html

from ..config import EASY, HARD, MIDDLE, VERY_EASY, VERY_HARD
from ..models import ItemZovgor

# fixme: adapt
LEVELS = {
    'низкая': VERY_EASY | EASY,
    'средняя': MIDDLE,
    'высокая': HARD | VERY_HARD,
}


async def parse_zovgor():
    page = await httpx.get('https://zovgor.com/shedule.html')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text.encode())
    titles = chain(
        tree.xpath('//*[@class="row-a"]/td[1]/a/text()'),
        tree.xpath('//*[@class="row-b"]/td[1]/a/text()'),
    )
    urls = chain(
        tree.xpath('//*[@class="row-a"]/td[1]/a/@href'),
        tree.xpath('//*[@class="row-b"]/td[1]/a/@href'),
    )
    dates = chain(
        tree.xpath('//*[@class="row-a"]/td[2]/text()'),
        tree.xpath('//*[@class="row-b"]/td[2]/text()'),
    )

    levels = chain(
        tree.xpath('//*[@class="row-a"]/td[4]/text()'),
        tree.xpath('//*[@class="row-b"]/td[4]/text()'),
    )

    parse_dt = partial(parse_date, datetime.now().year)
    data = zip(titles, urls, dates, levels)
    for title, url, date, level in data:
        start, end = map(parse_dt, date.split('-', 1))
        yield ItemZovgor(
            title=title,
            url='https://zovgor.com/' + url,
            level=LEVELS[level],
            start=start,
            end=end,
        )


def parse_date(now_year: int, src: str) -> datetime:
    date = lmap(int, src.split('.'))
    if len(date) == 2:
        (day, month), year = date, now_year
    else:
        day, month, year = date
        year = 2000 + year
    return datetime(year=year, month=month, day=day)
