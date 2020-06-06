import re
from datetime import datetime, timedelta
from functools import partial

import httpx

from ..config import CITYESCAPE, TODAY
from ..models import Item
from ..utils import gather_chunks, progress, silent

CITYESCAPE_URL = 'https://cityescape.ru/wp-admin/admin-ajax.php'
re_url = re.compile(r"""<a href=(['"]+)([^']+)\1""").findall


async def get_page(**kwargs):
    return await httpx.post(CITYESCAPE_URL, data=kwargs, timeout=20)


@progress
async def parse_cityescape(prog: progress):
    start = TODAY
    end = start + timedelta(days=365)
    prog('Getting index page')
    resp = await get_page(
        action='get_events',
        start=int(start.timestamp()),
        end=int(end.timestamp()),
    )
    parser = partial(parse_page, prog)
    return await gather_chunks(5, *map(parser, resp.json()))


@silent
async def parse_page(prog: progress, src: dict) -> Item:
    resp = await get_page(action='get_event', id=src['id'])
    data = resp.json()
    item = Item(
        vendor=CITYESCAPE,
        start=datetime.strptime(data['start'], '%m/%d/%Y %M:%H:%S'),
        end=datetime.strptime(data['end'], '%m/%d/%Y %M:%H:%S'),
        title=data['title'],
        url=re_url(data['content'])[0][1],
    )
    prog(item.url)
    return item
