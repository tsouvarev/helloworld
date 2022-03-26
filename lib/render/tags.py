import re
from dataclasses import asdict, dataclass, field
from functools import partial, reduce
from itertools import count
from typing import Callable, Dict, Iterable, List, Tuple

from funcy import post_processing

from ..config import SHORT_DURATION, TODAY, Currency, Level, Vendor
from ..utils import format_int
from .exchange import get_exchange, to_rub


@dataclass
class Tag:
    for_json = asdict
    slug: str
    text: str
    title: str = ''
    active: bool = False
    bit: int = field(init=False)
    index: int = field(init=False)

    def __and__(self, other):
        return self.bit & other

    __rand__ = __and__

    def __hash__(self):
        return hash(self.slug)


@dataclass
class TagGroup:
    slug: str
    tags: Iterable[Tag]
    title: str = ''
    index: int = field(  # type: ignore
        init=False,
        default_factory=partial(next, count(0)),
    )
    processors: List[Callable[['TagGroup'], None]] = field(
        default_factory=list
    )

    def __post_init__(self):
        for i, tag in enumerate(self.tags):
            tag.index = self.index
            tag.bit = 1 << i

    def __iter__(self):
        return (x for x in self.tags if x.active)

    def for_json(self):
        for p in self.processors:
            p(self)

        return {
            'title': self.title,
            'slug': self.slug,
            'tags': iter(self),
            'bits': reduce(lambda a, b: a | b.bit, self.tags, 0),
        }


def finder(pattern: str) -> Callable[[str], bool]:
    findall = re.compile(pattern, re.I).findall
    return lambda src: bool(findall(src))


def regroup(*args: str, begin: str = r'\b') -> str:
    return begin + '(%s)' % '|'.join(args)


NEW = Tag(slug='new', title='недавно добавленные', text='новые')
KIDS = Tag(slug='kids', title='с детьми', text='👶')
HIKING = Tag(slug='hiking', title='пеший', text='🥾')
kids_finder = finder(r'\b(семьи|семей|детск|[0-9]+\+)')
FinderDict = Dict[Tag, Callable[[str], bool]]

TYPES: FinderDict = {
    Tag(slug='rafting', title='сплав', text='🛶'): finder(
        r'\b(сплав|водн|байдар)'
    ),
    Tag(slug='bicycle', title='велопоход', text='🚴'): finder(r'\bвело'),
    Tag(slug='horse', title='конный', text='🐎'): finder(r'\bконны'),
    Tag(slug='snowmobile', title='на снегоходах', text='🛷'): finder(
        r'\b(снегоход[а-я]+)'
    ),
    Tag(slug='ski', title='лыжный', text='⛷️'): finder(
        r'\b((горнолыж|лыж)[а-я]+)'
    ),
    Tag(slug='pick', title='восхождение', text='⛏️'): finder(r'\bвосхожден'),
    Tag(slug='auto', title='автотур', text='🚗'): finder(
        r'\b(сафари|авто|джип|альпин)'
    ),
    Tag(slug='yoga', title='йога', text='🧘‍♂️'): finder(r'\bйог'),
    Tag(slug='freediving', title='фридайвинг', text='🤿'): finder(
        r'\bфридайвинг'
    ),
}

PLACES_RF: FinderDict = {
    Tag(slug='kamcha', text='камчатка'): finder(
        r'\b(камчат|толбач|сопк|командор|налыч|авач)'
    ),
    Tag(slug='sahalin', text='сахалин'): finder(
        r'\b(сахалин|курил|шикотан|итуруп)'
    ),
    Tag(slug='altay', text='алтай'): finder(
        r'\b(алта|мультинск|шавлинск|мааш|jайгы|чуйск)'
    ),
    Tag(slug='elbrus', text='эльбрус'): finder(r'эльбрус'),
    Tag(slug='baikal', text='байкал'): finder(r'байкал'),
    Tag(slug='south', text='юг'): finder(
        regroup(
            'крым',
            'севастопол',
            'краснодар',
            'соч[и,а]',
            'демердж',
            '-даг\b',
            'мезма',
            'красная поляна',
            'черн[а-я ]+мор[а-я]+',
            'таврид',
        )
    ),
    Tag(slug='north', text='север'): finder(
        regroup(
            'карел',
            'хибин',
            'мурманск',
            'териберк',
            'путоран',
            'ленобласт',
            r'ладо[г,ж]',
            'русский север',
            'ленинград',
            'питер',
            'петербур',
            'ловозер',
            'бел[а-я ]+мор[а-я]+',
            'кижи',
            'соловецк',
            'русская лапландия',
            r'сяпся\-шу[й,я]',
            'пистайоки',
            'сунск',
            'сейдозер',
        )
    ),
    Tag(slug='caucasus_rf', text='кавказ',): finder(
        regroup(
            'кавказ',
            'дагест',
            'архыз',
            'адыге',
            'абхаз',
            'чечн',
            'осети',
            'джилы',
            'пшеха',
            'ингушет',
            'тхач',
            r'лаго-наки',
            'кодор',
            'цейск',
            'чегем',
            'безенг',
            'домба[й,е]',
            'фишт',
            'софийск',
            'аксаут',
            'пастухов',
            'чедым',
            'имеретин',
        ),
    ),
    Tag(slug='arctica', text='арктика'): finder(r'(шпицберген|аркти|франца)'),
    Tag(
        slug='siberia',
        text='сибирь, урал, дв',
        title='Сибирь, Урал, Дальний Восток',
    ): finder(
        regroup(
            'якут',
            'тагана',
            'башкир',
            'сибир',
            'ольхон',
            'саян',
            'ергак',
            'маньпупунер',
            'урал',
            'дятлов',
            'хакас',
            'чукот',
            'амур',
            'шантар',
        )
    ),
}
OTHER_PLACES = Tag(slug='other_place', text='остальное')


PLACES_WORLD: FinderDict = {
    Tag(slug='turkey_cyprus', text='турция, кипр'): finder(
        r'\b(турци|каппадок|лики[й,я]|кипр)'
    ),
    Tag(slug='nepal', text='непал', title='Непал, Эеверест'): finder(
        r'\b(непал|эверест|аннапурн|мера[- ]пик|гимал)'
    ),
    Tag(slug='africa', text='африка'): finder(
        regroup(
            'алжир',
            'африк',
            'египет',
            'замби',
            'занзибар',
            'зимбабве',
            'кени[я,й,и]',
            'килиманджар',
            'конго',
            'мадагаскар',
            'марокк',
            'намиби',
            'нигер',
            'сейшел',
            'судан',
            'танзан',
            'тунис',
            'эфиоп',
            'юар',
            'eua',
            'тонга',
        )
    ),
    Tag(slug='america', text='америка'): finder(
        regroup(
            'америк',
            'аргентин',
            'болив',
            'бразил',
            'венесуэл',
            'галапагос',
            'доменикан',
            'колумб',
            'канад',
            'куб[а,е,и]',
            'мексик',
            'панам',
            'парагва',
            'перу',
            'сальвадор',
            'сша',
            'уругва',
            'чили',
            'эква',
            'ямайк',
            r'коста-рик',
        )
    ),
    Tag(
        slug='caucasus',
        text='кавказ',
        title='Армения, Азербайджан, Грузия',
    ): finder(
        r'\b(армен|грузи|сванети|азербайджан|казбек|тушет|хевсурет|чердым)'
    ),
    Tag(slug='asia', text='азия',): finder(
        regroup(
            'арави',
            'вьетнам',
            'израил',
            'инди',
            'индонез',
            'иордан',
            'иран',
            'камбодж',
            'китай',
            'коре[й,я]',
            'малайз',
            'мальдив',
            'мангол',
            'оаэ',
            'пакистан',
            'саудовск',
            'таиланд',
            'филиппин',
            r'шри-ланк',
            'япон',
        )
    ),
    Tag(
        slug='sng',
        text='снг',
        title='Киргизия, Таджикистан, Узбекистан, Казахстан, Украина',
    ): finder(r'\b(киргиз|таджик|узбек|казах|мангышлак|карпат|украин)'),
    Tag(slug='europe', text='европа'): finder(
        regroup(
            'австри',
            'агли',
            'азор',
            'белг',
            'болгар',
            'британ',
            'великобритан',
            'венгр',
            'герман',
            'голланд',
            'греци',
            'гренланд',
            'дани',
            'ирланд',
            'исланд',
            'испан',
            'итал',
            'латв',
            'литв',
            'мадейр',
            'нидерлагд',
            'норве',
            'польш',
            'португал',
            'румын',
            'финлянд',
            'франци',
            'черногор',
            'чехи',
            'швейцар',
            'швец',
            'шотланд',
            'эстон',
            'альп(?!и)',
            'аландск',
        )
    ),
}

SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')
VENDOR_TAGS = [
    Tag(slug=Vendor.PIK, text='пик'),
    Tag(slug=Vendor.ORANGEKED, text='оранжевый кед'),
    Tag(slug=Vendor.CITYESCAPE, text='cityescape'),
    Tag(slug=Vendor.ZOVGOR, text='зов гор'),
    Tag(slug=Vendor.NAPRAVLENIE, text='направление'),
    Tag(slug=Vendor.TEAMTRIP, text='team trip'),
    Tag(slug=Vendor.PEREHOD, text='переход'),
    Tag(slug=Vendor.STRANNIK, text='странник'),
    Tag(slug=Vendor.MYWAY, text='myway'),
    Tag(slug=Vendor.PRO_ADVENTURE, text='pro-adventure'),
    Tag(slug=Vendor.STRANAVETROV, text='страна ветров'),
]
VENDOR_MAP = {t.slug: t for t in VENDOR_TAGS}

LEVELS_TAGS = [
    Tag(slug='level_1', text='очень просто'),
    Tag(slug='level_2', text='просто'),
    Tag(slug='level_3', text='средней сложности'),
    Tag(slug='level_4', text='сложно'),
    Tag(slug='level_5', text='очень сложно'),
]

MONTH_TAGS = [
    Tag(slug='month_1', text='янв'),
    Tag(slug='month_2', text='фев'),
    Tag(slug='month_3', text='мар'),
    Tag(slug='month_4', text='апр'),
    Tag(slug='month_5', text='май'),
    Tag(slug='month_6', text='июн'),
    Tag(slug='month_7', text='июл'),
    Tag(slug='month_8', text='авг'),
    Tag(slug='month_9', text='сен'),
    Tag(slug='month_10', text='окт'),
    Tag(slug='month_11', text='ноя'),
    Tag(slug='month_12', text='дек'),
]

PRICE_TAGS = {
    5000: Tag(slug='5000', text='до ' + format_int(5000)),
    10000: Tag(slug='10000', text='до ' + format_int(10000)),
    30000: Tag(slug='30000', text='до ' + format_int(30000)),
    50000: Tag(slug='50000', text='до ' + format_int(50000)),
    70000: Tag(slug='70000', text='до ' + format_int(70000)),
    100000: Tag(slug='100000', text='до ' + format_int(100000)),
    999999: Tag(slug='999999', text='от ' + format_int(100000)),
}


def set_exchange(g: TagGroup):
    """
    Sets Central Bank Exchange rate as tag group title
    """

    g.title = '{} {}, {} {}'.format(
        Currency.USD,
        get_exchange()[Currency.USD],
        Currency.EUR,
        get_exchange()[Currency.EUR],
    )


TAGS: Tuple[TagGroup, ...] = (
    TagGroup(slug='vendors', tags=VENDOR_TAGS),
    TagGroup(slug='new', tags=[NEW]),
    TagGroup(slug='levels', title='Сложность', tags=LEVELS_TAGS),
    TagGroup(slug='age', tags=[KIDS]),
    TagGroup(slug='types', tags=list(TYPES) + [HIKING]),
    TagGroup(
        title='Продолжительность',
        slug='durations',
        tags=[SHORT, LONG],
    ),
    TagGroup(title='Месяц', slug='months', tags=MONTH_TAGS),
    TagGroup(
        title='Стоимость в рублях',
        slug='price',
        tags=PRICE_TAGS.values(),
        processors=[set_exchange],
    ),
    TagGroup(title='Россия', slug='places', tags=list(PLACES_RF)),
    TagGroup(
        title='Мир', slug='places', tags=list(PLACES_WORLD) + [OTHER_PLACES]
    ),
)


def reduce_bits(tags):
    result = [0] * len(TAGS)
    for tag in tags:
        tag.active = True
        result[tag.index] |= tag.bit
    return result


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDOR_MAP[src['vendor']]

    if src['new']:
        yield NEW

    for tag, find in TYPES.items():
        if find(src['norm']):
            yield tag
            break
    else:
        yield HIKING

    for tag, find in PLACES_RF.items():
        if find(src['norm']):
            yield tag
            break
    else:
        for tag, find in PLACES_WORLD.items():
            if find(src['norm']):
                yield tag
                break
        else:
            yield OTHER_PLACES

    # fixme: kids tag duck style
    level = src['level']
    if src['for_kids'] or kids_finder(src['norm']):
        yield KIDS
        if not level:
            # If guessed the level (i.e. eq is None),
            # then put EASY level,
            # cause it's for kids
            level = Level.EASY

    yield LEVELS_TAGS[(level or Level.MEDIUM) - 1]

    # duration
    if (src['end'] - src['start']) < SHORT_DURATION:
        yield SHORT
    else:
        yield LONG

    for m, month in enumerate(MONTH_TAGS, 1):
        start, end = src['start'].replace(day=1), src['end'].replace(day=1)

        date = TODAY.replace(month=m, day=1)
        if TODAY.month > m:
            date = date.replace(year=date.year + 1)

        if start <= date <= end:
            yield month

    price = to_rub(src['price'], src['currency'])
    if price:
        for k, v in PRICE_TAGS.items():
            tag = v
            if k >= price:
                yield tag
                break
