import pytest

from lib.render.tags import kids_finder
from lib.utils import normalize


@pytest.mark.parametrize(
    'src',
    (
        'Детский Кипр (4+)',
        'Мальдивы: весенний спортивно-образовательный лагерь для всей семьи',
        'Шри-Ланка: cемейный лагерь, синие киты и слоны',
        'Детская Грузия',
    ),
)
def test_re_kids(src):
    assert kids_finder(normalize(src))
