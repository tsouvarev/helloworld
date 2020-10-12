import re
from dataclasses import asdict, dataclass, field
from functools import partial, reduce
from itertools import count
from typing import Callable, Dict, List

from funcy import post_processing

from ..config import SHORT_DURATION, TODAY, Level, Vendor


@dataclass
class Tag:
    for_json = asdict
    slug: str
    text: str
    title: str = ''
    active: bool = False
    bit: int = field(init=False)
    index: int = field(init=False)

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
    index: int = field(init=False, default_factory=partial(next, count(0)))

    def __post_init__(self):
        for i, tag in enumerate(self.tags):
            tag.index = self.index
            tag.bit = 1 << i

    def __iter__(self):
        return iter(self.tags)

    def for_json(self):
        return {
            'title': self.title,
            'slug': self.slug,
            'tags': self.tags,
            'bits': reduce(lambda a, b: a | b.bit, self.tags, 0),
        }


def finder(pattern: str) -> Callable[[str], bool]:
    findall = re.compile(pattern, re.I).findall
    return lambda src: bool(findall(src))


NEW = Tag(slug='new', title='недавно добавленные', text='новые')
KIDS = Tag(slug='kids', title='с детьми', text='👶')
kids_finder = finder(r'\b(семьи|семей|детск|[0-9]+\+)')

TYPES: Dict[Tag, Callable[[str], bool]] = {
    Tag(slug='rafting', title='сплав', text='🛶'): finder(
        r'\b(сплав|водн|байдар)'
    ),
    Tag(slug='bicycle', title='велопоход', text='🚴'): finder(
        r'\b(велопоход|велосипед)'
    ),
}


SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')
VENDOR_TAGS = [
    Tag(slug=Vendor.PIK, text='пик'),
    Tag(slug=Vendor.ORANGEKED, text='оранжевый кед'),
    Tag(slug=Vendor.CITYESCAPE, text='cityescape'),
    Tag(slug=Vendor.ZOVGOR, text='зов гор'),
    Tag(slug=Vendor.NAPRAVLENIE, text='направление'),
    Tag(slug=Vendor.TEAMTRIP, text='team trip'),
    # Tag(slug=Vendor.POHODTUT, text='pohodtut'),
    Tag(slug=Vendor.PEREHOD, text='переход'),
    Tag(slug=Vendor.STRANNIK, text='странник'),
    Tag(slug=Vendor.MYWAY, text='myway'),
]
VENDOR_MAP = {t.slug: t for t in VENDOR_TAGS}

LEVELS_TAGS = [
    Tag(slug='level_1', text='очень просто'),
    Tag(slug='level_2', text='просто'),
    Tag(slug='level_3', text='средней сложности'),
    Tag(slug='level_4', text='сложно'),
    Tag(slug='level_5', text='очень сложно'),
]

MONTH_TAGS = [
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
]

TAGS = (
    TagGroup(slug='vendors', tags=VENDOR_TAGS),
    TagGroup(slug='new', tags=[NEW]),
    TagGroup(slug='levels', title='Сложность', tags=LEVELS_TAGS),
    TagGroup(slug='age', tags=[KIDS]),
    TagGroup(slug='type', tags=list(TYPES)),
    TagGroup(
        title='Продолжительность', slug='durations', tags=[SHORT, LONG],
    ),
    TagGroup(title='Месяц', slug='months', tags=MONTH_TAGS),
)


def reduce_bits(tags):
    result = [0] * len(TAGS)
    for tag in tags:
        tag.active = True
        result[tag.index] |= tag.bit
    return result


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDOR_MAP[src['vendor']]

    if src['new']:
        yield NEW

    for tag, find in TYPES.items():
        if find(src['norm']):
            yield tag
            break

    # fixme: kids tag duck style
    level = src['level']
    if src['for_kids'] or kids_finder(src['norm']):
        yield KIDS
        if not level:
            # If guessed the level (i.e. eq is None),
            # then put EASY level,
            # cause it's for kids
            level = Level.EASY

    yield LEVELS_TAGS[(level or Level.MEDIUM) - 1]

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
