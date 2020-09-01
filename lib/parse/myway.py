import re
from datetime import datetime
from typing import Iterator

from lxml import etree, html

from ..config import MONTHS, TODAY, Level, Vendor
from ..models import Item
from ..utils import content, css, zip_safe
from . import client

find_dates = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)').findall
find_dest = re.compile(r'([0-9]+)\s+км').findall

LEVELS = {
    'easy': Level.VERY_EASY,
    'complicated': Level.EASY,
    'normal': Level.MEDIUM,
    'hard': Level.HARD,
    'very_hard': Level.VERY_HARD,
}


async def parse_myway() -> Iterator[Item]:
    page = await client.get('https://mwtravel.ru/travel-all/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text)
    tails = (
        css('.alltravels .d-none .tour-line .title') + '/text()',
        css('.alltravels .d-none .tour-line .title') + '/@href',
        css('.alltravels .d-none .tour-line .info-wrapper .col'),
        css('.alltravels .d-none .tour-line .difficulty-link'),
        css('.alltravels .d-none .tour-line .dscr-wrapper'),
    )

    data = map(tree.xpath, tails)
    for title, href, dates, dif, descr in zip_safe(*data):
        description = etree.tostring(descr, encoding='utf8').decode().lower()
        start, end = parse_dates(content(dates))
        yield Item(
            vendor=Vendor.MYWAY,
            title=title.strip(),
            url=href,
            start=start,
            end=end,
            level=LEVELS[dif.get('id')],
            length=int(find_dest(description)[0]),
            for_kids='детьми' in description,
        )


def parse_date(src: str, orig: datetime) -> datetime:
    data = src.split()
    if len(data) == 3:
        day, mon, year = data
        month = MONTHS.index(mon) + 1
    elif len(data) == 2:
        (day, mon), year = data, orig.year
        month = MONTHS.index(mon) + 1
    else:
        day, month, year = data[0], orig.month, orig.year
    return datetime(day=int(day), month=month, year=int(year))


def parse_dates(src: str, orig: datetime = TODAY) -> Iterator[datetime]:
    _s, _e = src.lower().split('—')
    end = parse_date(_e, orig)
    yield parse_date(_s, end)
    yield end
