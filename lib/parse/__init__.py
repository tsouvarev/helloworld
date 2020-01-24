import asyncio
from datetime import datetime, timedelta
from functools import partial
from operator import attrgetter
from typing import Optional

from funcy import compose

from ..config import (
    CITYESCAPE,
    NAPRAVLENIE,
    ORANGEKED,
    PIK,
    TEAMTRIP,
    ZOVGOR,
    src_path,
)
from ..models import Item
from ..utils import info, json_dumps
from .cityescape import parse_cityescape
from .napravlenie import parse_napravlenie
from .orangeked import parse_orangeked
from .pik import parse_pik
from .teamtrip import parse_teamtrip
from .zovgor import parse_zovgor

NOW = datetime.now()
THIS_MONTH = NOW.replace(day=1)
TOO_LONG = timedelta(days=30)
TOO_FAR = NOW + timedelta(days=365)
VENDORS = {
    ORANGEKED: parse_orangeked,
    PIK: parse_pik,
    CITYESCAPE: parse_cityescape,
    ZOVGOR: parse_zovgor,
    NAPRAVLENIE: parse_napravlenie,
    TEAMTRIP: parse_teamtrip,
}


def is_valid(item: Optional[Item]):
    if item is None:
        # Failed to parse and silented
        return False

    if item.start < THIS_MONTH:
        info(f'Skip already started "{item.url}"')
        return False

    if item.end > TOO_FAR:
        info(f'Skip too far "{item.url}"')
        return False

    is_long = item.end - item.start >= TOO_LONG
    if is_long:
        info(f'Skip too long "{item.url}"')
        return False

    return True


prepare_items = compose(
    partial(sorted, key=attrgetter('start')), partial(filter, is_valid),
)


async def parse_async(*args: str):
    vendors = args or VENDORS
    for name in vendors:
        with open(src_path(name + '.json'), 'w+') as r:
            info(f'Parsing {name}...')
            items = prepare_items(await VENDORS[name]())
            info(f'Loaded {len(items)} items from {name}!')
            r.write(json_dumps(items))


def parse(vendor=()):
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async(*vendor))
