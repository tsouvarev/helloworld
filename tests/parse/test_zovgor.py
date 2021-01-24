from datetime import datetime

import pytest

from lib.parse.zovgor import parse_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            '06.03-18.03.22',
            [datetime(2022, 3, 6), datetime(2022, 3, 18)],
        ),
        (
            '25.10-01.11.21',
            [datetime(2021, 10, 25), datetime(2021, 11, 1)],
        ),
        (
            '25.12-05.01.22',
            [datetime(2021, 12, 25), datetime(2022, 1, 5)],
        ),
    ),
)
def test_split_dates(source, expected):
    result = list(parse_dates(source, datetime(2021, 1, 1)))
    assert result == expected
