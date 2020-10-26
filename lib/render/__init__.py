import json
from datetime import timedelta
from json import JSONDecodeError
from operator import itemgetter

from funcy import first
from typus import ru_typus

from ..config import (
    DIST_DATA,
    FIRST_DATE,
    LAST_DATE,
    META_DATA,
    NEW_INT,
    NO_WEEKENDS,
    TODAY,
    TODAY_INT,
    WEEKENDS,
    Vendor,
    src_path,
)
from ..utils import (
    debug,
    format_price,
    json_dumps,
    normalize,
    sorter,
    strptime,
)
from .tags import KIDS, TAGS, get_tags

TOO_LONG = timedelta(days=30)
CONSIDER_NEW = TODAY - timedelta(days=7)
JS_TEMPLATE = 'const DATA={{"weekendList": {}, "noWeekendList": {}, "eventSource": {}, "tagGroups": {}}};'
sort_items = sorter(itemgetter('start'))


def pre_filter(item: dict):
    if item['end'] > LAST_DATE:
        debug('Skip too far "{url}"'.format_map(item))
        return False

    is_long = item['end'] - item['start'] >= TOO_LONG
    if is_long:
        debug('Skip too long "{url}"'.format_map(item))
        return False
    return True


def post_filter(date, item: dict):
    if item['start'] < date:
        debug('Skip already started "{url}"'.format_map(item))
        return False
    return True


def parse_item(item: dict):
    item.update(
        start=strptime(item['start']), end=strptime(item['end']),
    )
    return item


def render_item(meta: dict, item: dict):
    item.update(
        price=item['price'] and format_price(item['price']),
        title=ru_typus(item['title'].strip('.')),
        norm=normalize(item['title']),
        new=meta[item['id']] >= NEW_INT,
    )
    # This must be called after all updates
    # to create valid tags
    item_tags = get_tags(item)
    item.update(
        tags=item_tags, for_kids=item_tags[3] & KIDS,
    )

    # fixme: time for pydantic
    item.pop('new')
    return item


def get_source():
    for v in Vendor:
        with open(src_path(v + '.json'), 'r') as f:
            yield from map(parse_item, json.load(f))


def render():
    """
    Renders data.json for index.html.
    """

    try:
        with open(META_DATA, 'r+') as f:
            meta = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        meta = {}

    with open(DIST_DATA, 'w+') as f:
        # - sorts and drops long items
        # - find earliest active
        # - filters items from earliest to make it pretty
        src_items = sort_items(filter(pre_filter, get_source()))
        earliest = first(
            x['start'] for x in src_items if x['end'] > FIRST_DATE
        )
        filtered = [x for x in src_items if post_filter(earliest, x)]
        new_meta = {i['id']: meta.get(i['id'], TODAY_INT) for i in filtered}

        # Writes data.js
        render_items = [render_item(new_meta, x) for x in filtered]
        dump = (WEEKENDS, NO_WEEKENDS, render_items, TAGS)
        template = JS_TEMPLATE.format(*map(json_dumps, dump))
        f.write(template)

    with open(META_DATA, 'w+') as f:
        f.write(json_dumps(new_meta))
