from datetime import datetime

from lib.config import Level
from lib.parse.pik import parse_item

ITEM_SOURCE = {
    'id': 2324,
    'vacancies': None,
    'is_full': False,
    'period_dates_humanized': 'с 20 по 23 фев 2021',
    'has_discount': False,
    'discount_cost_string': '0 ₽',
    'cost_string': '15 000 ₽',
    'start': '2021-02-20',
    'route': {
        'id': 474,
        'name': 'Активный Сочи',
        'slug': 'aktivnyi-sochi',
        'main_image': 'uploads/track_img/зима_на_берегу.png',
        'duration': 4,
        'path_length': 20,
        'short_description': 'FOO',
        'difficulty': {'name': 'Очень просто', 'slug': 'very_easy'},
        'types': [{'slug': 'peshiy'}],
        'from_cost_string': '15 000 ₽',
    },
}


def test_parse_item():
    item = parse_item(ITEM_SOURCE)
    assert item.title == 'Активный Сочи'
    assert item.price == '15 000 ₽'
    assert item.start == datetime(2021, 2, 20)
    assert item.end == datetime(2021, 2, 24)
    assert item.length == 20
    assert item.level == Level.VERY_EASY
