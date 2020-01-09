from datetime import date, datetime
from functools import partial

import simplejson

from .config import DATE_FORMAT


def strptime(src: str) -> datetime:
    return datetime.strptime(src, DATE_FORMAT)


def dumps_default(o):
    if isinstance(o, date):
        return o.strftime(DATE_FORMAT)
    raise TypeError


json_dumps = partial(
    simplejson.dumps,
    default=dumps_default,
    iterable_as_array=True,
    for_json=True,
    separators=(',', ':'),
)
