import pytest

from lib.utils import normalize


@pytest.mark.parametrize(
    'source, expected',
    (
        # EN + RU
        ('Cемейный отдых', 'семейный отдых'),
        ('Cемейный (  отдых)', 'семейный отдых'),
        # EN
        ('cat', 'cat'),
        ('cat3', 'cat3'),
    ),
)
def test_normalize(source, expected):
    assert normalize(source) == expected
