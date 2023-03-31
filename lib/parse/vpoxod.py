import re
from datetime import datetime
from typing import Iterator

from funcy import first
from lxml import html

from ..config import Level, Vendor
from ..models import Item
from ..utils import css, guess_currency, parse_int, zip_safe
from . import client

find_int = re.compile(r'\d+').findall


async def parse_vpoxod() -> Iterator[Item]:
    index = 1
    items = []
    seen = set()
    while True:
        url = f'https://www.vpoxod.ru/allroutes?sort=date&per-page=48&page={index}'
        page = await client.get(
            url,
            headers={
                "x-pjax": 'true',
                'x-pjax-container': '#routes-container',
                'x-requested-with': 'XMLHttpRequest',
            },
        )

        was = len(items)
        for item in parse_page(page.text):
            if item.id in seen:
                continue

            seen.add(item.id)
            items.append(item)

        if was == len(items):
            break

        index += 1

    return items


def parse_page(text) -> Item:
    tree = html.fromstring(text)
    props = tree.xpath('//*[@itemtype="https://schema.org/Event"]')
    headers = tree.find_class('item_header')
    bodies = tree.xpath(css('.item_header+tr'))

    for prop, header, body in zip_safe(props, headers, bodies):
        title = prop.find('meta[@itemprop="name"]').attrib['content']
        url = prop.find('meta[@itemprop="url"]').attrib['content']
        start = prop.find('meta[@itemprop="startDate"]').attrib['content']
        end = prop.find('meta[@itemprop="endDate"]').attrib['content']
        difficulty = len(header.find_class('difficulty-square fill'))
        price = body.find_class('table_price_right')[0].text_content()
        currency = prop.find('div/meta[@itemprop="priceCurrency"]').attrib[
            'content'
        ]
        slots = body.find_class('table_places')[0].text_content()
        if "мест нет" in slots:
            slots = 0
        else:
            slots = first(find_int(slots))

        yield Item(
            vendor=Vendor.VPOXOD,
            title=title,
            url=url,
            price=parse_int(price),
            currency=guess_currency(currency),
            start=parse_date(start),
            end=parse_date(end),
            slots=slots,
            level=Level.index(max(0, difficulty - 1)),
        )


def parse_date(src: str) -> datetime:
    return datetime.strptime(src, '%Y-%m-%d')
