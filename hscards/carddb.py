from   collections import defaultdict
from   enum        import Enum
from   functools   import total_ordering
from   itertools   import groupby
from   operator    import attrgetter
import textwrap

CARDS_URL = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'

class HSType(Enum):
    MINION      = 'Minion'
    SPELL       = 'Spell'
    WEAPON      = 'Weapon'
    HERO        = 'Hero'
    HERO_POWER  = 'Hero Power'
    ENCHANTMENT = 'Enchantment'

    def __str__(self):
        return self.value


class HSSet(Enum):
    CORE     = "Basic"
    EXPERT1  = "Classic"
    REWARD   = "Reward"
    PROMO    = "Promotion"
    HOF      = "Hall of Fame"
    NAXX     = "Curse of Naxxramas"
    GVG      = "Goblins vs. Gnomes"
    BRM      = "Blackrock Mountain"
    TGT      = "The Grand Tournament"
    LOE      = "League of Explorers"
    OG       = "Whispers of the Old Gods"
    KARA     = "Karazhan"
    GANGS    = "Mean Streets of Gadgetzan"
    UNGORO   = "Journey to Un'Goro"
    ICECROWN = "Knights of the Frozen Throne"
    LOOTAPALOOZA = "Kobolds & Catacombs"
    GILNEAS  = "The Witchwood"

    BLANK          = "BLANK"
    CHEAT          = "CHEAT"
    CREDITS        = "CREDITS"
    DEBUG_SP       = "DEBUG_SP"
    DEMO           = "DEMO"
    FP1            = "FP1"
    FP2            = "FP2"
    HERO_SKINS     = "Hero Skins"
    INVALID        = "INVALID"
    KARA_RESERVE   = "KARA_RESERVE"
    MISSIONS       = "MISSIONS"
    NONE           = "NONE"
    OG_RESERVE     = "OG_RESERVE"
    PE1            = "PE1"
    PE2            = "PE2"
    SLUSH          = "SLUSH"
    TB             = "Tavern Brawl"
    TEMP1          = "TEMP1"
    TEST_TEMPORARY = "TEST_TEMPORARY"

    def __str__(self):
        return self.value


class HSRace(Enum):
    ALL        = "All"
    BEAST      = "Beast"
    DEMON      = "Demon"
    DRAGON     = "Dragon"
    ELEMENTAL  = "Elemental"
    MECHANICAL = "Mech"
    MURLOC     = "Murloc"
    ORC        = "Orc"
    PIRATE     = "Pirate"
    TOTEM      = "Totem"

    def __str__(self):
        return self.value


class HSRarity(Enum):
    FREE      = 'Free'
    COMMON    = 'Common'
    RARE      = 'Rare'
    EPIC      = 'Epic'
    LEGENDARY = 'Legendary'

    def __str__(self):
        return self.value


@total_ordering
class HSClass(Enum):
    DRUID       = ('Druid', 0)
    HUNTER      = ('Hunter', 1)
    MAGE        = ('Mage', 2)
    PALADIN     = ('Paladin', 3)
    PRIEST      = ('Priest', 4)
    ROGUE       = ('Rogue', 5)
    SHAMAN      = ('Shaman', 6)
    WARLOCK     = ('Warlock', 7)
    WARRIOR     = ('Warrior', 8)
    NEUTRAL     = ('Neutral', 9)
    DREAM       = ('Emerald Dream', 10)
    DEATHKNIGHT = ('Death Knight', 11)

    def __str__(self):
        return self.value[0]

    def __lt__(self, other):
        if isinstance(other, HSClass):
            return self.value[1] < other.value[1]
        else:
            return NotImplemented


class HSCard:
    SPOILER_FIELDS = [
        ("Name",   "name"),
        ("Type",   "typeline"),
        ("Cost",   "cost"),
        ("Class",  "_classes"),
        ("Text",   "text"),
        ("Stats",  "statline"),
        ("Set",    "_set"),
        ("Flavor", "flavor"),
        ("Artist", "artist"),
    ]

    def __init__(self, data):
        # Ignored fields:
        #     dbfId            entourage         faction      howToEarn
        #     howToEarnGolden  id                mechanics    multiClassGroup
        #     overload         playRequirements  playerClass  referencedTags
        #     spellDamage      targetingArrowText
        for field in (
            'armor artist attack cost durability flavor health name text'
                .split()
        ):
            setattr(self, field, data.get(field))
        if "collectionText" in data:
            self.text = data["collectionText"]
        self.collectible = bool(data.get("collectible"))
        self.type = HSType[data["type"]]
        self.set  = HSSet[data["set"]]
        self.race = HSRace[data["race"]] if "race" in data else None
        if self.set == HSSet.CORE or "rarity" not in data:
            self.rarity = None
        else:
            self.rarity = HSRarity[data["rarity"]]
        self.card_class = HSClass[data["cardClass"]] if "cardClass" in data else None
        if "classes" in data:
            assert self.card_class is HSClass.NEUTRAL
            self.multi_classes = [HSClass[c] for c in data["classes"]]
        else:
            self.multi_classes = None

    @property
    def is_card(self):
        if self.type is HSType.HERO:
            # Objects of type "HERO" include:
            # - The nine basic heroes (in the CORE set)
            # - Alternate heroes (in the HERO_SKINS set)
            # - Adventure bosses (in their respective adventures' sets; not
            #   collectible)
            # - Hero cards (from ICECROWN onwards)
            return self.collectible and \
                self.set not in (HSSet.HERO_SKINS, HSSet.CORE)
        else:
            return self.type in (HSType.MINION, HSType.SPELL, HSType.WEAPON)

    def to_spoiler(self, columns=79, gutter=1):
        s = ''
        tagwidth = max(len(label) for label, _ in self.SPOILER_FIELDS) + 1
        valwidth = columns - tagwidth - gutter
        for name, attr in self.SPOILER_FIELDS:
            value = getattr(self, attr)
            if value is None or value == '':
                continue
            for i, ln in enumerate(wrap_lines(str(value).strip(), valwidth, 2)):
                tag = '' if i else name + ':'
                s += '{1:{0}}{3:{2}}{4}\n'.format(tagwidth, tag, gutter, '', ln)
        return s

    @property
    def typeline(self):
        sub = self.subtype
        if sub is not None:
            return '{} — {}'.format(self.type, sub)
        else:
            return str(self.type)

    @property
    def subtype(self):
        if self.type is HSType.MINION:
            return self.race
        elif self.type is HSType.SPELL:
            if (self.text or '').startswith('<b>Secret:</b>'):
                return 'Secret'
            elif '<b>Quest:</b>' in (self.text or ''):
                return 'Quest'
        return None

    @property
    def statline(self):
        if self.type is HSType.MINION:
            return '{0.attack:2}/{0.health:<2}'.format(self)
        elif self.type is HSType.WEAPON:
            return '{0.attack:2}/{0.durability:<2}'.format(self)
        elif self.type is HSType.HERO:
            return ' -/{0.armor:<2}'.format(self)
        else:
            return ''

    @property
    def _classes(self):
        if self.multi_classes is not None:
            return ', '.join(map(str, self.multi_classes))
        else:
            return str(self.card_class)

    @property
    def _set(self):
        if self.rarity is not None:
            return '{0.set} ({0.rarity})'.format(self)
        else:
            return str(self.set)

    def sort_key(self):
        return (self.card_class, self.cost, self.name)

    def checklist_columns(self):
        cols = [self.name, str(self.cost), self.typeline, self.statline]
        if self.rarity is not None:
            cols.append(str(self.rarity))
        return cols


class CardDB:
    def __init__(self, cards: [HSCard]):
        self.cards = list(cards)

    @classmethod
    def from_json(cls, cards: [dict]):
        hscards = []
        for c in cards:
            if "type" not in c:
                assert c["id"] == "PlaceholderCard"
                continue
            c = HSCard(c)
            if c.is_card and c.collectible:
                hscards.append(c)
        return cls(hscards)

    def __iter__(self):  # Cards in undefined order
        return iter(self.cards)

    def cards_sorted(self) -> [HSCard]:
        return sorted(self.cards, key=attrgetter("name"))

    def by_set(self) -> [(HSSet, [(HSClass, [HSCard])])]:
        # Sets are in undefined order
        # Classes within each set are in "checklist order"
        # Cards within each class are in "checklist order"
        cardsets = defaultdict(list)
        for c in self.cards:
            cardsets[c.set].append(c)
        for hs_set, cards in cardsets.items():
            cards.sort(key=HSCard.sort_key)
            yield (
                hs_set,
                [
                    (cls, list(cs))
                    for cls, cs in groupby(cards, attrgetter("card_class"))
                ],
            )


def wrap_lines(txt, length=80, postdent=0):
    lines = []
    for line in txt.rstrip().splitlines():
        line = line.rstrip()
        if line == '':
            lines.append('')
        else:
            lines.extend(textwrap.wrap(
                line, length,
                subsequent_indent=' ' * postdent,
                break_long_words=False,
                break_on_hyphens=False,
            ))
    return lines
