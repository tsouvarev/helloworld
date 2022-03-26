from datetime import datetime
from typing import Iterator

from funcy import invoke, partial
from lxml import html

from ..config import TODAY, Vendor
from ..models import Item
from ..utils import content, guess_currency, mapv, parse_int, zip_safe
from . import client


async def parse_zovgor() -> Iterator[Item]:
    page = await client.get('https://zovgor.com/shedule.html')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text.encode())
    path = '//*[@id="main"]/table/tbody/tr[position()>1]/'
    tails = (
        'td[1]/a[1]/@href',
        'td[2][descendant-or-self::text()]',
        'td[4]',
    )
    titles = [
        x
        for x in invoke(tree.xpath(path + 'td[1]'), 'text_content')
        if x != 'Пока нет в расписании'
    ]
    data = (tree.xpath(path + t) for t in tails)
    for title, url, date, price in zip_safe(titles, *data):
        price = content(price)
        start, end = parse_dates(content(date))
        yield Item(
            vendor=Vendor.ZOVGOR,
            title=title,
            url='https://zovgor.com/' + url,
            price=parse_int(price),
            currency=guess_currency(price),
            start=start,
            end=end,
        )


def parse_dates(src: str, today: datetime = TODAY):
    start, end = map(partial(parse_date, today=today), src.split('-', 1))
    if start.month <= end.month:
        start = start.replace(year=end.year)
    return start, end


def parse_date(src: str, today: datetime = TODAY) -> datetime:
    date = mapv(int, src.split('.'))
    if len(date) == 2:
        (day, month), year = date, today.year
    else:
        day, month, year = date
        year = 2000 + year
    return datetime(year=year, month=month, day=day)
