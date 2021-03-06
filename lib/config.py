import os.path
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from functools import partial

from funcy import nth

abs_path = partial(os.path.join, os.path.dirname(os.path.realpath(__file__)))
src_path = partial(abs_path, '../src')
www_path = partial(abs_path, '../docs')
DIST_DATA = www_path('data.js')
DIST_INDEX = www_path('index.html')
PREV_DATA = 'https://uhike.ru/data.js'

TODAY = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
FIRST_DATE = TODAY - timedelta(days=7)  # Makes render "today" on calendar
LAST_DATE = TODAY + timedelta(days=600)
TODAY_INT = int(TODAY.timestamp())
NEW_INT = int((TODAY - timedelta(days=2)).timestamp())

SHORT_DURATION = timedelta(days=3)
MONTHS_NORM = (
    'январь февраль март апрель май июнь июль август '
    'сентябрь октябрь ноябрь декабрь'.split()
)
MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)
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
    '24.06.2020',
    '01.07.2020',
    '04.11.2020',
    # 2021
    '01.01.2021',
    '02.01.2021',
    '03.01.2021',
    '04.01.2021',
    '05.01.2021',
    '06.01.2021',
    '07.01.2021',
    '08.01.2021',
    '22.02.2021',
    '23.02.2021',
    '08.03.2021',
    '03.05.2021',
    '10.05.2021',
    '14.06.2021',
    '04.11.2021',
    '31.12.2021',
]

NO_WEEKENDS = [
    '20.02.2021',
]


class Vendor(str, Enum):
    ORANGEKED = 'orangeked'
    PIK = 'pik'
    CITYESCAPE = 'cityescape'
    ZOVGOR = 'zovgor'
    NAPRAVLENIE = 'napravlenie'
    TEAMTRIP = 'teamtrip'
    PRO_ADVENTURE = 'pro_adventure'
    PEREHOD = 'perehod'
    STRANNIK = 'strannik'
    MYWAY = 'myway'
    STRANAVETROV = 'stranavetrov'


class Level(IntEnum):
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

    @classmethod
    def index(cls, key: int):
        return nth(key, iter(Level))
