import asyncio
from typing import Awaitable, Callable, Dict, Iterator, Sequence

from ..config import Vendor, src_path
from ..models import Item
from ..utils import compactv, info, json_dumps, progress
from .cityescape import parse_cityescape
from .client import Progress
from .napravlenie import parse_napravlenie
from .orangeked import parse_orangeked
from .pik import parse_pik
from .pohodtut import parse_pohodtut
from .teamtrip import parse_teamtrip
from .zovgor import parse_zovgor

# Parsers should fetch pages immediately and postpone parsing
# to log errors after progress bar is rendered
VENDORS: Dict[str, Callable[[], Awaitable[Iterator[Item]]]] = {
    Vendor.CITYESCAPE: parse_cityescape,
    Vendor.ORANGEKED: parse_orangeked,
    Vendor.PIK: parse_pik,
    Vendor.ZOVGOR: parse_zovgor,
    Vendor.NAPRAVLENIE: parse_napravlenie,
    Vendor.TEAMTRIP: parse_teamtrip,
    Vendor.POHODTUT: parse_pohodtut,
}


async def parse_gather(names: Sequence[str]):
    with progress() as p:
        Progress.set(p)
        results = await asyncio.gather(*(VENDORS[n]() for n in names))

    for name, res in zip(names, results):
        with open(src_path(name + '.json'), 'w+') as r:
            items = compactv(res)
            r.write(json_dumps(items))
            info(f'[{name}]: Loaded {len(items)} items')


def parse(vendor=()):
    """
    Loads data from websites.
    """
    asyncio.run(parse_gather(tuple(vendor or VENDORS)))
