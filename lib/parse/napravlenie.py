from datetime import datetime

import httpx
from lxml import html

from lib.config import NAPRAVLENIE
from lib.models import Item

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)


async def parse_napravlenie():
    page = await httpx.get('https://www.napravlenie.info/kalendar/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text)
    dates = tree.xpath('//*[@class="text-center cell date"]/div/text()')
    titles = tree.xpath('//*[@class="cell route"]/div/a/text()')
    hrefs = tree.xpath('//*[@class="cell route"]/div/a/@href')

    now = datetime.now()
    for date, title, href in zip(dates, titles, hrefs):
        start, end = parse_dates(now, date)
        yield Item(
            vendor=NAPRAVLENIE,
            start=start,
            end=end,
            title=title.replace(' / 2020', ''),
            url='https://www.napravlenie.info' + href,
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
