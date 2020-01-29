import pytest

from lib.parse.teamtrip import split_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            '15 - 27 июня, 28 июня - 10 июля, 2020',
            ['15 - 27 июня', '28 июня - 10 июля, 2020'],
        ),
        (
            '31 декабря, 2019 - 03 января, 2020 05 - 08 января / '
            '22 - 24 февраля / 07 - 09 марта, 2020',
            [
                '31 декабря, 2019 - 03 января, 2020',
                '05 - 08 января',
                '22 - 24 февраля',
                '07 - 09 марта, 2020',
            ],
        ),
    ),
)
def test_split_dates(source, expected):
    assert split_dates(source) == expected
