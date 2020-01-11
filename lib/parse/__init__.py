import asyncio

from ..config import CITYESCAPE, ORANGEKED, PIK, ZOVGOR, info, src_path
from ..utils import json_dumps
from .cityescape import parse_cityescape
from .orangeked import parse_orangeked
from .pik import parse_pik
from .zovgor import parse_zovgor

VENDORS = {
    ORANGEKED: parse_orangeked,
    PIK: parse_pik,
    CITYESCAPE: parse_cityescape,
    ZOVGOR: parse_zovgor,
}


async def parse_async(*args: str):
    vendors = args or VENDORS
    for name in vendors:
        with open(src_path(name + '.json'), 'w+') as r:
            info(f'Parsing {name}...')
            items = list(await VENDORS[name]())
            info(f'Loaded {len(items)} items from {name}!')
            r.write(json_dumps(items))


def parse(vendor=()):
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async(*vendor))
