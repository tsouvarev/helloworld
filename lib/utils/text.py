import re

from funcy import compact, joining

NORM = str.maketrans(
    {
        'e': 'е',
        'y': 'у',
        'o': 'о',
        'p': 'р',
        'a': 'а',
        'h': 'н',
        'k': 'к',
        'x': 'х',
        'c': 'с',
        'b': 'в',
        'm': 'м',
        'ё': 'е',
    }
)

RE_MISTYPES = re.compile(r'\b()\b', re.I)
RE_SPLIT = re.compile(r'\W+', re.U).split
RE_CYRILLIC = re.compile(r'[а-яё]').findall


@joining(' ')
def normalize(string: str):
    words = compact(RE_SPLIT(string.lower()))
    for word in words:
        if RE_CYRILLIC(word):
            yield word.translate(NORM)
        else:
            yield word
