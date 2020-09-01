from datetime import datetime
from typing import Iterator

from funcy import partial
from lxml import html

from ..config import TODAY, Vendor
from ..models import Item
from ..utils import content, mapv, zip_safe
from . import client


async def parse_zovgor() -> Iterator[Item]:
    page = await client.get('https://zovgor.com/shedule.html')
    return parse_page(page.text)


def parse_page(text):
    parse_dt = partial(parse_date, TODAY.year)
    tree = html.fromstring(text.encode())
    path = '//*[@id="main"]/table/tbody/tr[position()>1]/'
    tails = (
        'td[1]',
        'td[1]/a[1]/@href',
        'td[2][descendant-or-self::text()]',
        'td[4]/text()',
    )
    data = (tree.xpath(path + t) for t in tails)
    for title, url, date, price in zip_safe(*data):
        start, end = map(parse_dt, content(date).split('-', 1))
        yield Item(
            vendor=Vendor.ZOVGOR,
            title=title.text_content(),
            url='https://zovgor.com/' + url,
            price=price,
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
