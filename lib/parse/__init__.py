import asyncio
from functools import partial
from operator import attrgetter
from typing import Awaitable, Callable, Dict, Iterator, Sequence

from ..config import Vendor, src_path
from ..models import Item
from ..utils import compact, distinctv, info, json_dumps, progress
from .cityescape import parse_cityescape
from .client import Progress
from .myway import parse_myway
from .napravlenie import parse_napravlenie
from .orangeked import parse_orangeked
from .perehod import parse_perehod
from .pik import parse_pik
from .pohodtut import parse_pohodtut
from .strannik import parse_strannik
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
    # Vendor.POHODTUT: parse_pohodtut,
    Vendor.PEREHOD: parse_perehod,
    Vendor.STRANNIK: parse_strannik,
    Vendor.MYWAY: parse_myway,
}

unique_items = partial(distinctv, attrgetter('url', 'start', 'end'))


async def parse_gather(names: Sequence[str]):
    with progress() as p:
        Progress.set(p)
        results = await asyncio.gather(*(VENDORS[n]() for n in names))

    for name, res in zip(names, results):
        path = src_path(name + '.json')
        with open(path, 'w+') as f:
            items = unique_items(compact(res))
            f.write(json_dumps(items))
            info(f'[{name}]: Loaded {len(items)} items')


def parse(vendor=()):
    """
    Loads data from websites.
    """
    asyncio.run(parse_gather(tuple(vendor or VENDORS)))
