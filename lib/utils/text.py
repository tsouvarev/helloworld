import re
from typing import Optional

from funcy import compact, joining, partial

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


re_digits = partial(re.compile(r'\D+').sub, '')
DEFAULT_CURRENCY = f'{{}}{NBSP}₽'
CURRENCIES = {
    f'€{NBSP}{{}}': re.compile(r'(€|евро|eur)', re.I),
    f'${NBSP}{{}}': re.compile(r'(\$|дол|usd)', re.I),
    DEFAULT_CURRENCY: re.compile(r'(₽|руб|р\.?)', re.I),
}


def guess_currency(src: str, default=DEFAULT_CURRENCY) -> str:
    for key, value in CURRENCIES.items():
        if value.search(src):
            return key
    return default


def format_price(src: str):
    price = int_or_none(src)
    if not price:
        # nothing found
        return src

    currency = guess_currency(src)
    return currency.format(format_int(price))


def int_or_none(src: str) -> Optional[int]:
    try:
        return int(re_digits(src))
    except ValueError:
        return None
