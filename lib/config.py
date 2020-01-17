import os.path
from datetime import timedelta
from functools import partial

abs_path = partial(os.path.join, os.path.dirname(os.path.realpath(__file__)))
src_path = partial(abs_path, '../src')
DIST_DATA = abs_path('../www/data.js')

ORANGEKED = 'orangeked'
PIK = 'pik'
CITYESCAPE = 'cityescape'
ZOVGOR = 'zovgor'
NAPRAVLENIE = 'napravlenie'
VENDORS = (ORANGEKED, PIK, CITYESCAPE, ZOVGOR, NAPRAVLENIE)

DATE_FORMAT = '%d.%m.%Y'
SHORT_DURATION = timedelta(days=3)
WEEKENDS = [
    '01.01.2020',
    '02.01.2020',
    '03.01.2020',
    '06.01.2020',
    '07.01.2020',
    '08.01.2020',
    '03.01.2020',
    '24.02.2020',
    '09.03.2020',
    '01.05.2020',
    '04.05.2020',
    '05.05.2020',
    '11.05.2020',
    '12.06.2020',
    '04.11.2020',
]

VERY_EASY = 1 << 1
EASY = 1 << 2
MIDDLE = 1 << 3
HARD = 1 << 4
VERY_HARD = 1 << 5
LEVELS = (
    VERY_EASY,
    EASY,
    MIDDLE,
    HARD,
    VERY_HARD,
)
