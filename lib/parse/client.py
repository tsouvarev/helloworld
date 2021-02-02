from contextvars import ContextVar
from functools import partial
from typing import Awaitable, Callable

import httpx

from ..utils import progress

Progress: ContextVar[progress] = ContextVar('Prog')


async def request(
    method: str, url: str, *args, timeout: int = 30, **kwargs
) -> httpx.Response:
    abspath = url
    try:
        async with httpx.AsyncClient(verify=False) as c:
            resp = await c.request(
                method, url, *args, timeout=timeout, **kwargs
            )
            if resp.url:
                abspath = str(resp.url)
            return resp
    finally:
        prog = Progress.get()
        prog(abspath)


MethType = Callable[..., Awaitable[httpx.Response]]
get: MethType = partial(request, 'GET')
post: MethType = partial(request, 'POST')
