import asyncio
import re
from datetime import datetime, timedelta

import httpx
from funcy import chain, chunks

from ..config import CITYESCAPE
from ..models import Item

CITYESCAPE_URL = 'https://cityescape.ru/wp-admin/admin-ajax.php'
RE_URL = re.compile(r"""<a href=(['"]+)([^']+)\1""").findall


async def get_page(**kwargs):
    return await httpx.post(CITYESCAPE_URL, data=kwargs, timeout=20)


async def get_event(item: dict) -> dict:
    resp = await get_page(action='get_event', id=item['id'])
    return resp.json()


async def parse_cityescape():
    start = datetime.utcnow()
    end = start + timedelta(days=365)
    resp = await get_page(
        action='get_events',
        start=int(start.timestamp()),
        end=int(end.timestamp()),
    )

    items = []
    for chunk in chunks(5, resp.json()):
        items = chain(items, await asyncio.gather(*map(get_event, chunk)))
    return map(parse_item, items)


def parse_item(item: dict) -> Item:
    return Item(
        vendor=CITYESCAPE,
        start=datetime.strptime(item['start'], '%m/%d/%Y %M:%H:%S'),
        end=datetime.strptime(item['end'], '%m/%d/%Y %M:%H:%S'),
        title=item['title'],
        url=RE_URL(item['content'])[0][1],
    )
