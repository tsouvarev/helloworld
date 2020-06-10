from datetime import datetime

import pytest

from lib.parse.pohodtut import parse_date


@pytest.mark.parametrize(
    'source, expected',
    (
        ('24 июня', (datetime(2020, 6, 24), datetime(2020, 6, 24))),
        ('17 июля - 19 июля', (datetime(2020, 7, 17), datetime(2020, 7, 19))),
        ('24 июля - 26 июля', (datetime(2020, 7, 24), datetime(2020, 7, 26))),
        ('11 июля - 12 июля', (datetime(2020, 7, 11), datetime(2020, 7, 12))),
        ('20 июня - 21 июня', (datetime(2020, 6, 20), datetime(2020, 6, 21))),
        ('14 июня', (datetime(2020, 6, 14), datetime(2020, 6, 14))),
        ('16 июня', (datetime(2020, 6, 16), datetime(2020, 6, 16))),
        ('11 июня - 13 июня', (datetime(2020, 6, 11), datetime(2020, 6, 13))),
    ),
)
def test_parse_date(source, expected):
    today = datetime(2020, 6, 10)
    assert tuple(parse_date(source, today)) == expected
