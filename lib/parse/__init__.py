import asyncio

from ..config import SRC_ORANGEKED, SRC_PIK
from ..utils import json_dumps
from .orangeked import parse_orangeked
from .pik import parse_pik


async def parse_async():
    with open(SRC_ORANGEKED, 'w+') as r:
        r.write(json_dumps(await parse_orangeked()))

    with open(SRC_PIK, 'w+') as r:
        r.write(json_dumps(await parse_pik()))


def parse():
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async())
