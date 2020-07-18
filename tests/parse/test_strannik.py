import pytest

from lib.parse.strannik import clear_days


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            'Поход на байдарках по реке Угра. 5 дней. ',
            'Поход на байдарках по реке Угра',
        ),
        ('Поход по среднему Битюгу. 2 дня.', 'Поход по среднему Битюгу'),
        (
            'На байдарках и катамаранах по Суне (Ю. Карелия).7дней.',
            'На байдарках и катамаранах по Суне (Ю. Карелия)',
        ),
        (
            'Поход на байдарках по реке Пра. 4 дня',
            'Поход на байдарках по реке Пра',
        ),
    ),
)
def test_clear_days(source, expected):
    assert clear_days(source) == expected
