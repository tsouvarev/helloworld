import pytest

from lib.render.tags import RE_KIDS
from lib.utils import normalize


@pytest.mark.parametrize(
    'src',
    (
        'Детский Кипр (4+)',
        'Мальдивы: весенний спортивно-образовательный лагерь для всей семьи',
        'Шри-Ланка: cемейный лагерь, синие киты и слоны',
    ),
)
def test_re_kids(src):
    assert RE_KIDS(normalize(src))
