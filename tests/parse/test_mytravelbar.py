from datetime import datetime

import pytest

from lib.parse.mytravelbar import parse_date


@pytest.mark.parametrize(
    'source, expected',
    (
        ('7 ИЮНЯ (ВС)', [datetime(2020, 6, 7), datetime(2020, 6, 7)]),
        ('28 ИЮНЯ (ВС)', [datetime(2020, 6, 28), datetime(2020, 6, 28)]),
        (
            '13 – 14 ИЮНЯ (СБ-ВС)',
            [datetime(2020, 6, 13), datetime(2020, 6, 14)],
        ),
    ),
)
def test_parse_date(source, expected):
    now = datetime(2020, 6, 5)
    assert list(parse_date(now, source)) == expected
