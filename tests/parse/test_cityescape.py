# flake8: noqa

from datetime import datetime

import pytest

from lib.parse.cityescape import TITLE_RE, parse_dates


@pytest.mark.parametrize(
    'source, expected',
    (
        ('К мельнице по берегам Протвы 24 июня 2020', '24 июня 2020'),
        (
            'Поход в каньон Бунчихи — горной речки Подмосковья 4-5 июля 2020',
            '4-5 июля 2020',
        ),
        ('Марш-бросок к Змеиному камню 5 июля 2020', '5 июля 2020',),
        (
            'Поход к Введенскому Островному монастырю 26 июля 2020',
            '26 июля 2020',
        ),
        (
            'Поход в Тарусу по берегам Оки 22-23 августа 2020',
            '22-23 августа 2020',
        ),
        (
            'Пеший поход в Коломну через городище Ростиславль Рязанский 5-6 сентября 2020',
            '5-6 сентября 2020',
        ),
        (
            'Сплав по реке Сестра 27 июня, 1 июля 2020',
            '27 июня, 1 июля 2020',
        ),
        ('Сплав по реке Нерская 1 июля 2020', '1 июля 2020',),
        (
            'Сплав по реке Клязьма 18-19 июля, 8-9 августа 2020',
            '18-19 июля, 8-9 августа 2020',
        ),
        (
            'Водный поход по Великим озерам Тверской области 17-19 июля 2020',
            '17-19 июля 2020',
        ),
        (
            'Сплав по реке Киржач 27-28 июня, 15-16 августа 2020',
            '27-28 июня, 15-16 августа 2020',
        ),
        (
            'Сплав по реке Угра 11-12 июля, 15-16 августа 2020',
            '11-12 июля, 15-16 августа 2020',
        ),
        (
            'Сплав на байдарках по Шатурским озерам 4 июля, 5 июля 2020',
            '4 июля, 5 июля 2020',
        ),
        (
            'Восхождение на Белуху 26 июля - 8 августа 2020',
            '26 июля - 8 августа 2020',
        ),
        (
            'Путешествие в Армению и восхождение на Арагац 22 сентября - 1 октября 2020',
            '22 сентября - 1 октября 2020',
        ),
        (
            'Поход в Архыз по хребту Абишира-Ахуба 24 июля-1 августа 2020',
            '24 июля-1 августа 2020',
        ),
        (
            'Восхождение на Эльбрус с севера 3-13 июля 2020, 15-25 августа 2020',
            '3-13 июля 2020, 15-25 августа 2020',
        ),
    ),
)
def test_title_re(source, expected):
    [(title, dates)] = TITLE_RE.findall(source)
    assert dates == expected
    assert f'{title} {dates}' == source


@pytest.mark.parametrize(
    'source, expected',
    (
        (
            '24 июня 2020',
            [
                (
                    datetime(year=2020, month=6, day=24),
                    datetime(year=2020, month=6, day=24),
                )
            ],
        ),
        (
            '20-31 июля 2020',
            [
                (
                    datetime(year=2020, month=7, day=20),
                    datetime(year=2020, month=7, day=31),
                )
            ],
        ),
        (
            '31 октября-8 ноября 2020',
            [
                (
                    datetime(year=2020, month=10, day=31),
                    datetime(year=2020, month=11, day=8),
                )
            ],
        ),
        (
            '27 июня, 1 июля 2020',
            [
                (
                    datetime(year=2020, month=6, day=27),
                    datetime(year=2020, month=6, day=27),
                ),
                (
                    datetime(year=2020, month=7, day=1),
                    datetime(year=2020, month=7, day=1),
                ),
            ],
        ),
        (
            '18-19 июля, 8-9 августа 2020',
            [
                (
                    datetime(year=2020, month=7, day=18),
                    datetime(year=2020, month=7, day=19),
                ),
                (
                    datetime(year=2020, month=8, day=8),
                    datetime(year=2020, month=8, day=9),
                ),
            ],
        ),
        (
            '26 июля - 8 августа 2020',
            [
                (
                    datetime(year=2020, month=7, day=26),
                    datetime(year=2020, month=8, day=8),
                )
            ],
        ),
        (
            '24 июля-1 августа 2020',
            [
                (
                    datetime(year=2020, month=7, day=24),
                    datetime(year=2020, month=8, day=1),
                )
            ],
        ),
        (
            '3-13 июля 2020, 15-25 августа 2020',
            [
                (
                    datetime(year=2020, month=7, day=3),
                    datetime(year=2020, month=7, day=13),
                ),
                (
                    datetime(year=2020, month=8, day=15),
                    datetime(year=2020, month=8, day=25),
                ),
            ],
        ),
        (
            '3 декабря - 13 января 2021, 3 декабря - 13 января 2021, 3 декабря 2020 - 13 января 2021',
            [
                (
                    datetime(year=2020, month=12, day=3),
                    datetime(year=2021, month=1, day=13),
                ),
                (
                    datetime(year=2020, month=12, day=3),
                    datetime(year=2021, month=1, day=13),
                ),
                (
                    datetime(year=2020, month=12, day=3),
                    datetime(year=2021, month=1, day=13),
                ),
            ],
        ),
    ),
)
def test_parse_dates(source, expected):
    assert list(parse_dates(source)) == expected
