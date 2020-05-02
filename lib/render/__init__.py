import json
from datetime import datetime, timedelta
from operator import itemgetter

from funcy import first, pluck
from typus import ru_typus

from ..config import DIST_DATA, VENDORS, WEEKENDS, src_path
from ..utils import debug, error, json_dumps, normalize, sorter, strptime
from .tags import LEVELS_TAGS, TAGS, get_tags

NOW = datetime.now()
TOO_LONG = timedelta(days=30)
TOO_FAR = NOW + timedelta(days=420)
JS_TEMPLATE = (
    'const DATA={{"weekendList": {}, "eventSource": {}, "tagGroups": {}}};'
)
sort_items = sorter(itemgetter('start'))


def pre_filter(item: dict):
    if item['end'] > TOO_FAR:
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
        title=ru_typus(item['title']),
        norm=normalize(item['title']),
        start=strptime(item['start']),
        end=strptime(item['end']),
    )
    # This mast be after all updates
    # to create valid tags
    item.update(tags=get_tags(item))

    # Replaces bit level with first matching human level
    item.update(
        level=first(
            i for i, x in enumerate(LEVELS_TAGS, 1) if item['tags'] & x.bit
        )
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

    with open(DIST_DATA, 'r+') as f:
        try:
            file = f.read()[11:-1]
            seen = set(pluck('url', json.loads(file)['eventSource']))
        except Exception as e:
            error(str(e))
            seen = set()
        finally:
            f.seek(0)

        # clean shit
        f.truncate()

        # - sorts and drops long items
        # - find earliest active
        # - filters items from earliest to make it pretty
        items = sort_items(filter(pre_filter, get_source()))
        earliest = first(x['start'] for x in items if x['end'] > NOW)
        filtered = [x for x in items if post_filter(earliest, x)]

        # todo: send to telegram
        arrived = set(pluck('url', filtered)) - seen
        if seen and arrived:
            debug('New items found! 🎉')
            for item in arrived:
                debug('- ' + item)

        # Writes data.js
        dumped = map(json_dumps, (WEEKENDS, filtered, TAGS))
        template = JS_TEMPLATE.format(*dumped)
        f.write(template)
