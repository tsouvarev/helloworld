import os.path
from datetime import timedelta
from functools import partial

abs_path = partial(os.path.join, os.path.dirname(os.path.realpath(__file__)))
src_path = partial(abs_path, '../src')
www_path = partial(abs_path, '../www')
META_DATA = src_path('__meta__.json')
DIST_DATA = www_path('data.js')
DIST_INDEX = www_path('index.html')

ORANGEKED = 'orangeked'
PIK = 'pik'
CITYESCAPE = 'cityescape'
ZOVGOR = 'zovgor'
NAPRAVLENIE = 'napravlenie'
TEAMTRIP = 'teamtrip'
VENDORS = (ORANGEKED, PIK, CITYESCAPE, ZOVGOR, NAPRAVLENIE, TEAMTRIP)

DATE_FORMAT = '%d.%m.%Y'
SHORT_DURATION = timedelta(days=3)
WEEKENDS = [
    # 2020
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
    # 2021
    '01.01.2021',
    '02.01.2021',
    '03.01.2021',
    '06.01.2021',
    '07.01.2021',
    '08.01.2021',
    '23.02.2021',
    '08.03.2021',
    '03.05.2021',
    '10.05.2021',
    '14.06.2021',
    '04.11.2021',
]

# Some events do match several levels,
# that are bit for.
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
DEFAULT_LEVEL = MIDDLE
