import json

from lib.utils import strptime


def parse_item(item: dict):
    item.update(
        start=strptime(item['start']), end=strptime(item['end']),
    )
    return item


def pik_data(src):
    with open(src, 'r') as f:
        items = json.load(f)
        return map(parse_item, items)
