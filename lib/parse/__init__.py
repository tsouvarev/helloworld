import asyncio

from ..config import Vendor, src_path
from ..utils import compactv, debug, info, json_dumps
from .cityescape import parse_cityescape
from .mytravelbar import parse_mytravelbar
from .napravlenie import parse_napravlenie
from .orangeked import parse_orangeked
from .pik import parse_pik
from .teamtrip import parse_teamtrip
from .zovgor import parse_zovgor

VENDORS = {
    Vendor.CITYESCAPE: parse_cityescape,
    Vendor.ORANGEKED: parse_orangeked,
    Vendor.PIK: parse_pik,
    Vendor.ZOVGOR: parse_zovgor,
    Vendor.NAPRAVLENIE: parse_napravlenie,
    Vendor.TEAMTRIP: parse_teamtrip,
    Vendor.MYTRAVELBAR: parse_mytravelbar,
}


async def parse_async(*args: str):
    vendors = args or VENDORS
    for name in vendors:
        with open(src_path(name + '.json'), 'w+') as r:
            info(f'Parsing {name}...')
            items = compactv(await VENDORS[name]())
            debug(f'Loaded {len(items)} items from {name}!')
            r.write(json_dumps(items))


def parse(vendor=()):
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async(*vendor))
