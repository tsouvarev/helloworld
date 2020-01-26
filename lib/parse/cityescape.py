import re
from datetime import datetime, timedelta

import httpx

from ..config import CITYESCAPE
from ..models import Item
from ..utils import gather_chunks, silent

CITYESCAPE_URL = 'https://cityescape.ru/wp-admin/admin-ajax.php'
RE_URL = re.compile(r"""<a href=(['"]+)([^']+)\1""").findall


async def get_page(**kwargs):
    return await httpx.post(CITYESCAPE_URL, data=kwargs, timeout=20)


async def parse_cityescape():
    start = datetime.utcnow()
    end = start + timedelta(days=365)
    resp = await get_page(
        action='get_events',
        start=int(start.timestamp()),
        end=int(end.timestamp()),
    )

    return await gather_chunks(5, *map(parse_page, resp.json()))


@silent
async def parse_page(item: dict) -> Item:
    resp = await get_page(action='get_event', id=item['id'])
    data = resp.json()
    return Item(
        vendor=CITYESCAPE,
        start=datetime.strptime(data['start'], '%m/%d/%Y %M:%H:%S'),
        end=datetime.strptime(data['end'], '%m/%d/%Y %M:%H:%S'),
        title=data['title'],
        url=RE_URL(data['content'])[0][1],
    )
