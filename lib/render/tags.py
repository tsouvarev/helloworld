import re
from dataclasses import asdict, dataclass, field
from enum import IntEnum, unique
from typing import List

from funcy import post_processing

from ..config import SHORT_DURATION, TODAY, Level, Vendor


@unique
class Bit(IntEnum):
    kids = 1 << 0
    short = 1 << 1
    long = 1 << 2
    pik = 1 << 3
    orangeked = 1 << 4
    cityescape = 1 << 5
    zovgor = 1 << 6
    napravlenie = 1 << 7
    teamtrip = 1 << 8
    level_1 = 1 << 9
    level_2 = 1 << 10
    level_3 = 1 << 11
    level_4 = 1 << 12
    level_5 = 1 << 13
    month_1 = 1 << 14
    month_2 = 1 << 15
    month_3 = 1 << 16
    month_4 = 1 << 17
    month_5 = 1 << 18
    month_6 = 1 << 19
    month_7 = 1 << 20
    month_8 = 1 << 21
    month_9 = 1 << 22
    month_10 = 1 << 23
    month_11 = 1 << 24
    month_12 = 1 << 25
    rafting = 1 << 26
    pohodtut = 1 << 27
    bicycle = 1 << 28


@dataclass
class Tag:
    for_json = asdict
    slug: str
    text: str
    title: str = ''
    active: bool = False
    bit: Bit = field(init=False)

    def __post_init__(self):
        self.bit = Bit[self.slug]

    def __and__(self, other):
        return self.bit & other

    __rand__ = __and__

    def __hash__(self):
        return hash(self.slug)


@dataclass(frozen=True)
class TagGroup:
    slug: str
    tags: List[Tag]
    title: str = ''

    def __iter__(self):
        return iter(self.tags)

    def for_json(self):
        return {
            'title': self.title,
            'slug': self.slug,
            'tags': self.tags,
            'bits': reduce_bits(self.tags),
        }


KIDS = Tag(slug='kids', title='с детьми', text='👶')
RAFTING = Tag(slug='rafting', title='сплав', text='🛶')
BICYCLE = Tag(slug='bicycle', title='велопоход', text='🚴')
TYPES = {
    KIDS: re.compile(r'\b(семьи|семей|детск|[0-9]+\+)', re.I).findall,
    RAFTING: re.compile(r'\b(сплав|водн)', re.I).findall,
    BICYCLE: re.compile(r'\b(велопоход|велосипед)', re.I).findall,
}


SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')

VENDOR_TAGS = TagGroup(
    slug='vendors',
    tags=[
        Tag(slug=Vendor.PIK, text='пик'),
        Tag(slug=Vendor.ORANGEKED, text='оранжевый кед'),
        Tag(slug=Vendor.CITYESCAPE, text='cityescape'),
        Tag(slug=Vendor.ZOVGOR, text='зов гор'),
        Tag(slug=Vendor.NAPRAVLENIE, text='направление'),
        Tag(slug=Vendor.TEAMTRIP, text='team trip'),
        Tag(slug=Vendor.POHODTUT, text='pohodtut'),
    ],
)

VENDOR_MAP = {t.slug: t for t in VENDOR_TAGS}

LEVELS_TAGS = TagGroup(
    title='Сложность',
    slug='levels',
    tags=[
        Tag(slug='level_1', text='очень просто'),
        Tag(slug='level_2', text='просто'),
        Tag(slug='level_3', text='средней сложности'),
        Tag(slug='level_4', text='сложно'),
        Tag(slug='level_5', text='очень сложно'),
    ],
)

MONTH_TAGS = TagGroup(
    title='Месяц',
    slug='months',
    tags=[
        Tag(slug='month_1', text='янв'),
        Tag(slug='month_2', text='фев'),
        Tag(slug='month_3', text='мар'),
        Tag(slug='month_4', text='апр'),
        Tag(slug='month_5', text='май'),
        Tag(slug='month_6', text='июн'),
        Tag(slug='month_7', text='июл'),
        Tag(slug='month_8', text='авг'),
        Tag(slug='month_9', text='сен'),
        Tag(slug='month_10', text='окт'),
        Tag(slug='month_11', text='ноя'),
        Tag(slug='month_12', text='дек'),
    ],
)

TAGS = (
    VENDOR_TAGS,
    LEVELS_TAGS,
    TagGroup(slug='type', tags=list(TYPES)),
    TagGroup(title='Продолжительность', slug='durations', tags=[SHORT, LONG]),
    MONTH_TAGS,
)


def reduce_bits(tags):
    result = 0
    for tag in tags:
        tag.active = True
        result |= tag.bit
    return result


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDOR_MAP[src['vendor']]

    # fixme: kids tag duck style
    level = src['level']
    for tag, finder in TYPES.items():
        if not finder(src['norm']):
            continue

        yield tag

        if tag is KIDS and not level:
            # If guessed the level (i.e. eq is None),
            # then put EASY level,
            # cause it's for kids
            level = Level.EASY

    yield LEVELS_TAGS.tags[(level or Level.MEDIUM) - 1]

    # duration
    if (src['end'] - src['start']) < SHORT_DURATION:
        yield SHORT
    else:
        yield LONG

    for m, month in enumerate(MONTH_TAGS, 1):
        start, end = src['start'].replace(day=1), src['end'].replace(day=1)

        date = TODAY.replace(month=m, day=1)
        if TODAY.month > m:
            date = date.replace(year=date.year + 1)

        if start <= date <= end:
            yield month
