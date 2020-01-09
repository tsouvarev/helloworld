import operator
import re
from dataclasses import asdict, dataclass, field
from functools import partial, reduce
from itertools import count
from typing import Dict

from funcy import post_processing

from ..config import SHORT_DURATION

bits = partial(next, count(1))


@dataclass
class Tag:
    for_json = asdict

    slug: str
    text: str
    title: str = ''
    bit: int = field(default_factory=lambda: 1 << bits())
    active: bool = True


class TagGroup:
    tags: Dict[str, Tag]

    def __init__(self, *tags: Tag):
        self.tags = {t.slug: t for t in tags}

    def __getitem__(self, item: str):
        return self.tags[item]

    def for_json(self):
        tags = self.tags.values()
        return {
            'tags': tags,
            'bits': reduce_bits(tags),
        }


PIK = Tag(slug='pik', text='пик')
ORANGEKED = Tag(slug='orangeked', text='оранжевый кед')
LEVEL_1 = Tag(slug='level_1', text='очень просто')
LEVEL_2 = Tag(slug='level_2', text='просто')
LEVEL_3 = Tag(slug='level_3', text='средней сложности')
LEVEL_4 = Tag(slug='level_4', text='сложно')
LEVEL_5 = Tag(slug='level_5', text='очень сложно')
KIDS = Tag(slug='kids', title='с детьми', text='👶')
SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')

VENDORS = TagGroup(PIK, ORANGEKED,)

LEVELS = TagGroup(LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5,)

TAGS = (
    VENDORS,
    LEVELS,
    TagGroup(SHORT, LONG),
    TagGroup(KIDS),
)


def reduce_bits(tags):
    return reduce(operator.or_, (t.bit for t in tags))


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDORS[src['vendor']]
    yield LEVELS['level_{level}'.format_map(src)]

    # fixme: kids tag duck style
    if re.findall(r'(семей|\([0-9]+\+\))', src['title'], re.I):
        yield KIDS

    # duration
    if (src['end'] - src['start']) <= SHORT_DURATION:
        yield SHORT
    else:
        yield LONG
