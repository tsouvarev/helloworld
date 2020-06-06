import json
import time
from datetime import timedelta
from json import JSONDecodeError
from operator import itemgetter

from funcy import first
from typus import ru_typus

from ..config import (
    DIST_DATA,
    LAST_DATE,
    META_DATA,
    TODAY,
    VENDORS,
    WEEKENDS,
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
from .tags import KIDS, LEVELS_TAGS, TAGS, get_tags

TOO_LONG = timedelta(days=30)
CONSIDER_NEW = TODAY - timedelta(days=7)
JS_TEMPLATE = (
    'const DATA={{"weekendList": {}, "eventSource": {}, "tagGroups": {}}};'
)
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


def post_filter(now, item: dict):
    if item['start'] < now:
        debug('Skip already started "{url}"'.format_map(item))
        return False
    return True


def parse_item(item: dict):
    item.update(
        start=strptime(item['start']), end=strptime(item['end']),
    )
    return item


def render_item(item: dict):
    item.update(
        price=item['price'] and format_price(item['price']),
        title=ru_typus(item['title'].strip('.')),
        norm=normalize(item['title']),
    )
    # This mast be after all updates
    # to create valid tags
    item_tags = get_tags(item)
    item.update(tags=item_tags)

    # Replaces bit level with first matching int level
    item.update(
        for_kids=KIDS & item_tags,
        level=first(i for i, x in enumerate(LEVELS_TAGS, 1) if x & item_tags),
    )
    return item


def get_source():
    for v in VENDORS:
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
        items = sort_items(filter(pre_filter, get_source()))
        earliest = first(x['start'] for x in items if x['end'] > TODAY)
        filtered = [x for x in items if post_filter(earliest, x)]

        new_meta = {}
        now = int(time.time())
        for item in items:
            created = meta.get(item['id'], now)
            new_meta[item['id']] = created

            # Not new,
            # but really first time seen
            if created is now:
                debug('🎉 {url}'.format_map(item))

        # Writes data.js
        dumped = map(json_dumps, (WEEKENDS, map(render_item, filtered), TAGS))
        template = JS_TEMPLATE.format(*dumped)
        f.write(template)

    with open(META_DATA, 'w+') as f:
        f.write(json_dumps(new_meta))
