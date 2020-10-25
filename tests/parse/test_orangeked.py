from datetime import datetime

import pytest

from lib.parse.orangeked import parse_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        ('17 июля - 19 июля', (datetime(2021, 7, 17), datetime(2021, 7, 19))),
        ('20 - 21 июня', (datetime(2021, 6, 20), datetime(2021, 6, 21))),
        (
            '11 октября - 13 ноября',
            (datetime(2020, 10, 11), datetime(2020, 11, 13)),
        ),
    ),
)
def test_parse_dates(source, expected):
    today = datetime(2020, 10, 2)
    assert tuple(parse_dates(source, today)) == expected
