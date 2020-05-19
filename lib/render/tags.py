import re
from dataclasses import asdict, dataclass, field
from functools import partial
from itertools import count
from typing import List

from funcy import cat, post_processing

from ..config import (
    CITYESCAPE,
    DEFAULT_LEVEL,
    EASY,
    LAST_DATE,
    LEVELS,
    NAPRAVLENIE,
    NOW,
    ORANGEKED,
    PIK,
    SHORT_DURATION,
    TEAMTRIP,
    ZOVGOR,
)

bits = partial(next, count())


@dataclass
class Tag:
    for_json = asdict
    slug: str
    text: str
    title: str = ''
    bit: int = field(default_factory=lambda: 1 << bits())
    active: bool = False

    def __and__(self, other):
        return self.bit & other

    __rand__ = __and__


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
SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')

VENDOR_TAGS = TagGroup(
    slug='vendors',
    tags=[
        Tag(slug=PIK, text='пик'),
        Tag(slug=ORANGEKED, text='оранжевый кед'),
        Tag(slug=CITYESCAPE, text='клуб походов и приключений'),
        Tag(slug=ZOVGOR, text='зов гор'),
        Tag(slug=NAPRAVLENIE, text='направление'),
        Tag(slug=TEAMTRIP, text='team trip'),
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

MONTHS_NAMES = 'янв фев мар апр май июн июл авг сен окт ноя дек'.split()
MONTH_TAGS = TagGroup(
    title='Месяц, год',
    slug='months',
    tags=[
        Tag(slug=f'month_{i}', text=m) for i, m in enumerate(MONTHS_NAMES, 1)
    ],
)
YEAR_NUMS = range(NOW.year, LAST_DATE.year)
YEAR_TAGS = TagGroup(
    slug='years',
    tags=[
        Tag(slug=f'year_{x}', text=f'<small>{x}</small>') for x in YEAR_NUMS
    ],
)

TAGS = (
    VENDOR_TAGS,
    LEVELS_TAGS,
    TagGroup(slug='kids', tags=[KIDS]),
    TagGroup(title='Продолжительность', slug='durations', tags=[SHORT, LONG]),
    MONTH_TAGS,
    YEAR_TAGS,
)


def reduce_bits(tags):
    result = 0
    for tag in tags:
        tag.active = True
        result |= tag.bit
    return result


re_kids = re.compile(r'(семьи|семей|детск|[0-9]+\+)', re.I).findall


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDOR_MAP[src['vendor']]

    # fixme: kids tag duck style
    level = src['level']
    if re_kids(src['norm']):
        yield KIDS

        # If guessed the level (i.e. eq to DEFAULT_LEVEL),
        # then put EASY level,
        # cause it's for kids
        if level == DEFAULT_LEVEL:
            level = EASY

    for bit, tag in zip(LEVELS, LEVELS_TAGS):
        if bit & level:
            yield tag

    # duration
    if (src['end'] - src['start']) <= SHORT_DURATION:
        yield SHORT
    else:
        yield LONG

    for m, month in enumerate(MONTH_TAGS, 1):
        if src['start'].month <= m <= src['end'].month:
            yield month

    for year, tag in zip(YEAR_NUMS, YEAR_TAGS):
        if src['start'].year == year or src['end'].year == year:
            yield tag
