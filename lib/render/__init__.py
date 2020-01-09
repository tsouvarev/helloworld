from functools import partial
from itertools import chain
from operator import itemgetter

from ..config import DIST_DATA, SRC_ORANGEKED, SRC_PIK, WEEKENDS, info
from ..utils import json_dumps
from .orangeked import orangeked_data
from .pik import pik_data
from .tags import TAGS, get_tags

JS_TEMPLATE = 'let weekendList = {}, eventSource = {}; tagGroups = {}'
sort_data = partial(sorted, key=itemgetter('start'))


def prepare(src: dict):
    return dict(src, tags=get_tags(src))


def render():
    """
    Renders data.json for index.html.
    """

    info('Rendering...')
    source = chain(orangeked_data(SRC_ORANGEKED), pik_data(SRC_PIK),)
    data = sort_data(map(prepare, source))
    with open(DIST_DATA, 'w+') as f:
        template = JS_TEMPLATE.format(
            json_dumps(WEEKENDS), json_dumps(data), json_dumps(TAGS),
        )
        f.write(template)
