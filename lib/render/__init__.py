import json
from functools import partial
from operator import itemgetter

from funcy import post_processing

from ..config import DIST_DATA, VENDORS, WEEKENDS, info, src_path
from ..utils import json_dumps, strptime
from .tags import TAGS, get_tags

sort_data = partial(sorted, key=itemgetter('start'))
JS_TEMPLATE = 'let weekendList = {}, eventSource = {}; tagGroups = {}'


def parse_item(item: dict):
    item.update(
        start=strptime(item['start']), end=strptime(item['end']),
    )
    item['tags'] = get_tags(item)
    return item


@post_processing(sort_data)
def get_source():
    for v in VENDORS:
        with open(src_path(v + '.json'), 'r') as f:
            yield from map(parse_item, json.load(f))


def render():
    """
    Renders data.json for index.html.
    """

    info('Rendering...')
    with open(DIST_DATA, 'w+') as f:
        template = JS_TEMPLATE.format(
            json_dumps(WEEKENDS), json_dumps(get_source()), json_dumps(TAGS),
        )
        f.write(template)
