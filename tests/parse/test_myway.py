from datetime import datetime

import pytest

from lib.parse.myway import parse_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            '15 — 21 Сентября 2020',
            (datetime(2020, 9, 15), datetime(2020, 9, 21)),
        ),
        (
            '31 Декабря 2020 — 4 Января 2021',
            (datetime(2020, 12, 31), datetime(2021, 1, 4)),
        ),
        ('4 — 22 Января 2021', (datetime(2021, 1, 4), datetime(2021, 1, 22))),
    ),
)
def test_parse_dates(source, expected):
    today = datetime(2020, 6, 10)
    assert tuple(parse_dates(source, today)) == expected
