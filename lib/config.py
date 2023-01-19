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
    # 2023
    '01.01.2023',
    '02.01.2023',
    '03.01.2023',
    '04.01.2023',
    '05.01.2023',
    '06.01.2023',
    '07.01.2023',
    '08.01.2023',
    '23.02.2023',
    '24.02.2023',
    '08.03.2023',
    '01.05.2023',
    '08.05.2023',
    '09.05.2023',
    '12.06.2023',
    '06.11.2023',
]

NO_WEEKENDS = []


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
    VPOXOD = 'vpoxod'


class Level(IntEnum):
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

    @classmethod
    def index(cls, key: int):
        return nth(key, iter(Level))


class Currency(str, Enum):
    RUB = '₽'
    EUR = '€'
    USD = '$'
