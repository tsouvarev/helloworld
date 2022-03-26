from functools import lru_cache
from math import ceil
from typing import Dict

import httpx

from ..config import Currency

CURRENCIES = {
    Currency.EUR.name: Currency.EUR,
    Currency.USD.name: Currency.USD,
}


@lru_cache(1)
def get_exchange() -> Dict[str, int]:
    resp = httpx.get('https://www.cbr-xml-daily.ru/daily_json.js')
    values = resp.json()['Valute']
    return {
        CURRENCIES[k]: ceil(v['Value'])
        for k, v in values.items()
        if k in CURRENCIES
    }


def to_rub(price: int, currency: str) -> int:
    if currency != Currency.RUB:
        return price * get_exchange()[currency]
    return price
