from datetime import datetime

import pytest

from lib.parse.teamtrip import parse_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            '15 - 27 июня, 28 июня - 10 июля, 2020',
            [
                (datetime(2020, 6, 15), datetime(2020, 6, 27)),
                (datetime(2020, 6, 28), datetime(2020, 7, 10)),
            ],
        ),
        (
            '31 декабря, 2019 - 03 января, 2020 05 - 08 января / '
            '22 - 24 февраля / 07 - 09 марта, 2020',
            [
                (datetime(2019, 12, 31), datetime(2020, 1, 3)),
                (datetime(2020, 1, 5), datetime(2020, 1, 8)),
                (datetime(2020, 2, 22), datetime(2020, 2, 24)),
                (datetime(2020, 3, 7), datetime(2020, 3, 9)),
            ],
        ),
        (
            '30.10 - 07.11 / 09.11 - 17.11 / 20.11 - 28.11',
            [
                (datetime(2020, 10, 30), datetime(2020, 11, 7)),
                (datetime(2020, 11, 9), datetime(2020, 11, 17)),
                (datetime(2020, 11, 20), datetime(2020, 11, 28)),
            ],
        ),
        (
            'декабрь 2020 / 31.12 - 03.01 / 04 - 07 января / '
            '07 - 10 января / 20 - 23 февраля / 05 - 08 марта',
            [
                (datetime(2020, 12, 31), datetime(2020, 1, 3)),
                (datetime(2020, 1, 4), datetime(2020, 1, 7)),
                (datetime(2020, 1, 7), datetime(2020, 1, 10)),
                (datetime(2020, 2, 20), datetime(2020, 2, 23)),
                (datetime(2020, 3, 5), datetime(2020, 3, 8)),
            ],
        ),
        (
            '28 июля — 7 августа',
            [(datetime(2020, 7, 28), datetime(2020, 8, 7))],
        ),
        (
            '08 - 16 сентября,15 - 23 сентября, 2021',
            [
                (datetime(2020, 9, 8), datetime(2020, 9, 16)),
                (datetime(2021, 9, 15), datetime(2021, 9, 23)),
            ],
        ),
    ),
)
def test_split_dates(source, expected):
    result = list(parse_dates(source, datetime(2020, 1, 1)))
    assert result == expected
