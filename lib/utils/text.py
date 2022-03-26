import re
from contextlib import suppress
from typing import Dict, Optional

from funcy import compact, joining, partial

from ..config import Currency

NBSP = '\u00A0'
NORM = str.maketrans(
    {
        'e': 'е',
        'y': 'у',
        'o': 'о',
        'p': 'р',
        'a': 'а',
        'h': 'н',
        'k': 'к',
        'x': 'х',
        'c': 'с',
        'b': 'в',
        'm': 'м',
        'ё': 'е',
    }
)

RE_MISTYPES = re.compile(r'\b()\b', re.I)
RE_SPLIT = re.compile(r'[^\w\+-]+', re.U).split
RE_CYRILLIC = re.compile(r'[а-яё]').findall
RE_DIGITS = partial(re.compile(r'\D+').sub, '')


@joining(' ')
def normalize(string: str):
    words = compact(RE_SPLIT(string.lower()))
    for word in words:
        if RE_CYRILLIC(word):
            yield word.translate(NORM)
        else:
            yield word


def format_int(src: int) -> str:
    return '{:,}'.format(src).replace(',', NBSP)


CURRENCIES: Dict[Currency, re.Pattern] = {
    Currency.EUR: re.compile(r'(€|евро|eur)', re.I),
    Currency.USD: re.compile(r'(\$|дол|usd)', re.I),
    Currency.RUB: re.compile(r'(₽|руб|р\.?)', re.I),
}

CURRENCIES_FORMATS: Dict[Currency, str] = {
    Currency.EUR: f'{Currency.EUR}{NBSP}{{}}',
    Currency.USD: f'{Currency.USD}{NBSP}{{}}',
    Currency.RUB: f'{{}}{NBSP}{Currency.RUB}',
}


def guess_currency(src: str) -> Currency:
    for key, value in CURRENCIES.items():
        if value.search(src):
            return key
    return Currency.RUB


def format_price(price: int, currency: Currency) -> str:
    return CURRENCIES_FORMATS[currency].format(format_int(price))


def int_or_none(src: str) -> Optional[int]:
    try:
        return int(RE_DIGITS(src))
    except ValueError:
        return None


def parse_int(src: str) -> int:
    with suppress(ValueError):
        return int(RE_DIGITS(src))
    return 0
