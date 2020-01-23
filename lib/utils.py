from contextlib import contextmanager
from datetime import date, datetime
from functools import partial, update_wrapper
from inspect import iscoroutinefunction

import click
import simplejson
from funcy import compose

from .config import DATE_FORMAT

info = partial(click.secho, color='white', bold=True)
error = partial(click.secho, color='red', err=True)
compact = partial(filter, bool)
compactv = compose(list, compact)
filterv = compose(list, filter)
mapv = compose(list, map)


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
            f'"{func.__name__}" failed with "{e}", '
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
