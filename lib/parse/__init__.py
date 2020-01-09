import asyncio

from ..config import SRC_PIK
from ..utils import json_dumps
from .pik import parse_pik


async def parse_async():
    result = json_dumps(await parse_pik())
    with open(SRC_PIK, 'w+') as r:
        r.write(result)


def parse():
    """
    Loads data from websites.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_async())
