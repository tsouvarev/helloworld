import asyncio
from datetime import timedelta

from ..config import CITYESCAPE, NAPRAVLENIE, ORANGEKED, PIK, ZOVGOR, src_path
from ..models import Item
from ..utils import compact, filterv, info, json_dumps
from .cityescape import parse_cityescape
from .napravlenie import parse_napravlenie
from .orangeked import parse_orangeked
from .pik import parse_pik
from .zovgor import parse_zovgor

TOO_LONG = timedelta(days=30)
VENDORS = {
    ORANGEKED: parse_orangeked,
    PIK: parse_pik,
    CITYESCAPE: parse_cityescape,
    ZOVGOR: parse_zovgor,
    NAPRAVLENIE: parse_napravlenie,
}


def short_item(item: Item):
    is_short = item.end - item.start < TOO_LONG
    if not is_short:
        info(f'Skip too long "{item.url}"')
    return is_short


async def parse_async(*args: str):
    vendors = args or VENDORS
    for name in vendors:
        with open(src_path(name + '.json'), 'w+') as r:
            info(f'Parsing {name}...')
            items = filterv(short_item, compact(await VENDORS[name]()))
            info(f'Loaded {len(items)} items from {name}!')
            r.write(json_dumps(items))


def parse(vendor=()):
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async(*vendor))
