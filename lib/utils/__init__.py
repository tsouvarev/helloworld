import asyncio
import calendar
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from functools import partial, update_wrapper, wraps
from inspect import iscoroutinefunction
from itertools import cycle, zip_longest
from typing import Callable, Iterable, Iterator, Optional

import click
import simplejson
from cssselect import GenericTranslator
from funcy import cat, chunks, compose
from funcy.primitives import EMPTY

from .text import format_price, int_or_none, normalize, re_digits  # noqa

debug = click.secho
info = partial(click.secho, color='white', bold=True)
warn = partial(click.secho, color='yellow')
error = partial(click.secho, fg='red', err=True, bold=True)
filterv = compose(list, filter)
compact = partial(filter, bool)
compactv = compose(list, compact)
mapv = compose(list, map)
css = GenericTranslator().css_to_xpath

ERASE_LINE = '\x1b[2K'


@dataclass
class progress:
    spinner: Iterator = field(default_factory=partial(cycle, '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'))

    def __new__(cls, func: Optional[Callable] = None):
        inst = super().__new__(cls)
        if not func:
            return inst

        @wraps(func)
        async def inner(*args, **kwargs):
            with inst as prog:
                return await func(prog, *args, **kwargs)

        # If __new__() does not return an instance of cls,
        # then the new instance’s __init__() method will not be invoked.
        cls.__init__(inst)
        return inner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(ERASE_LINE, end='\r', flush=True)

    def __call__(self, msg: str):
        spin = next(self.spinner)
        print(f'{ERASE_LINE}\r{spin} {msg}', end='')


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def dumps_default(o):
    if isinstance(o, date):
        return calendar.timegm(o.timetuple())
    raise TypeError


json_loads = simplejson.loads
json_dumps = partial(
    simplejson.dumps,
    default=dumps_default,
    iterable_as_array=True,
    for_json=True,
    sort_keys=True,
    indent=0,
    separators=(',', ':'),
)


@contextmanager
def log_exception(func, args, kwargs):
    try:
        yield
    except Exception as e:
        error(
            f'"{func.__name__}" failed with "{e!r}", '
            f'called with {args} and {kwargs}'
        )


def silent(func):
    if iscoroutinefunction(func):

        async def inner(*args, **kwargs):
            with log_exception(func, args, kwargs):
                return await func(*args, **kwargs)

    else:

        def inner(*args, **kwargs):
            with log_exception(func, args, kwargs):
                return func(*args, **kwargs)

    return update_wrapper(inner, func)


def sorter(func):
    return partial(sorted, key=func)


def zip_safe(*its: Iterable):
    for item in zip_longest(*its, fillvalue=EMPTY):
        if EMPTY in item:
            raise ValueError('Failed safe zip')
        yield item


async def gather_chunks(size: int, *coros, return_exceptions=False):
    gather = partial(asyncio.gather, return_exceptions=return_exceptions)
    return cat([await gather(*c) for c in chunks(size, coros)])


def hash_uid(src: str, maxlen: int = 7) -> str:
    return hashlib.sha256(src.encode()).hexdigest()[:maxlen]


def content(e) -> str:
    return e.text_content().strip()


def distinct(key: Optional[Callable] = None, items: Iterable = ()):
    seen = set()
    getter = key or (lambda x: x)
    for item in items:
        value = getter(item)
        if value not in seen:
            seen.add(value)
            yield item


distinctv = compose(list, distinct)
