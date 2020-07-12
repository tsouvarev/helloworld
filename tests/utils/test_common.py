import pytest
from funcy import chunks

from lib.utils import zip_safe


@pytest.mark.parametrize(
    'source, expected',
    (
        ([(0, 1), (2, 3)], [(0, 2), (1, 3)]),
        (chunks(2, range(4)), [(0, 2), (1, 3)]),
    ),
)
def test_zip_safe_ok(source, expected):
    assert list(zip_safe(*source)) == expected


def test_zip_safe_fails():
    with pytest.raises(ValueError):
        list(zip_safe((0, 1), (2,)))
