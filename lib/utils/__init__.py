import asyncio
import operator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import partial, update_wrapper
from inspect import iscoroutinefunction
from itertools import cycle, zip_longest
from typing import Iterable, Iterator

import click
import simplejson
from funcy import cat, chunks, compose
from funcy.primitives import EMPTY

from ..config import DATE_FORMAT
from .text import format_price, normalize  # noqa

debug = click.secho
info = partial(click.secho, color='white', bold=True)
error = partial(click.secho, fg='red', err=True, bold=True)
filterv = compose(list, filter)
compactv = partial(filterv, bool)
mapv = compose(list, map)
is_empty = partial(operator.is_, EMPTY)
any_empty = compose(any, partial(filter, is_empty))

ERASE_LINE = '\x1b[2K'


@dataclass
class progress:
    spinner: Iterator = field(default_factory=partial(cycle, '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(ERASE_LINE, end='\r', flush=True)

    def __call__(self, msg: str):
        spin = next(self.spinner)
        print(f'{ERASE_LINE}\r{spin} {msg}', end='')


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
    sort_keys=True,
    indent=4,
    separators=(',', ': '),
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
        if any_empty(item):
            raise ValueError('Failed safe zip')
        yield item


async def gather_chunks(size: int, *coros, return_exceptions=False):
    gather = partial(asyncio.gather, return_exceptions=return_exceptions)
    return cat([await gather(*c) for c in chunks(size, coros)])
