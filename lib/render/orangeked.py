import json
from datetime import datetime

from lib.config import DATE_FORMAT


def orangeked_data(src):
    with open(src, 'r') as f:
        items = json.load(f)
        for item in items:
            item['start'] = datetime.strptime(item['start'], DATE_FORMAT)
            item['end'] = datetime.strptime(item['end'], DATE_FORMAT)
            yield item
