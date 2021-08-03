from   collections import defaultdict
from   enum        import Enum
from   functools   import total_ordering
from   itertools   import groupby
import json
from   operator    import attrgetter
from   pathlib     import Path
import re
import textwrap

CARDS_URL = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'

BASIC_JSON = Path(__file__).with_name('basic.json')

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
    CORE     = "Core"
    VANILLA  = "Classic"
    EXPERT1  = "Classic Set"
    LEGACY   = "Legacy"
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
    BOOMSDAY = "The Boomsday Project"
    TROLL    = "Rastakhan's Rumble"
    DALARAN  = "Rise of Shadows"
    ULDUM    = "Saviors of Uldum"
    DRAGONS  = "Descent of Dragons"
    YEAR_OF_THE_DRAGON = "Galakrond's Awakening"
    DEMON_HUNTER_INITIATE = "Demon Hunter Initiate"
    BLACK_TEMPLE = "Ashes of Outland"
    SCHOLOMANCE = "Scholomance Academy"
    DARKMOON_FAIRE = "Madness at the Darkmoon Faire"
    THE_BARRENS = "Forged in the Barrens"
    STORMWIND = "United in Stormwind"

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
    QUILBOAR   = "Quilboar"
    TOTEM      = "Totem"

    def __str__(self):
        return self.value


class HSSchool(Enum):
    ARCANE = "Arcane"
    FIRE   = "Fire"
    FROST  = "Frost"
    NATURE = "Nature"
    HOLY   = "Holy"
    SHADOW = "Shadow"
    FEL    = "Fel"

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
    DEMONHUNTER = ('Demon Hunter', 0)
    DRUID       = ('Druid', 1)
    HUNTER      = ('Hunter', 2)
    MAGE        = ('Mage', 3)
    PALADIN     = ('Paladin', 4)
    PRIEST      = ('Priest', 5)
    ROGUE       = ('Rogue', 6)
    SHAMAN      = ('Shaman', 7)
    WARLOCK     = ('Warlock', 8)
    WARRIOR     = ('Warrior', 9)
    NEUTRAL     = ('Neutral', 10)
    DREAM       = ('Emerald Dream', 11)
    DEATHKNIGHT = ('Death Knight', 12)

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
        #     howToEarnGolden  mechanics         multiClassGroup
        #     overload         playRequirements  playerClass  referencedTags
        #     spellDamage      targetingArrowText
        for field in (
            'armor artist attack cost durability flavor health id name'
            ' gold_class gold_levels unlock_lvl'  # From basic.json
            .split()
        ):
            setattr(self, field, data.get(field))
        if "collectionText" in data and \
                not data["name"].startswith('Galakrond,'):
            self.text = sanitize(data["collectionText"])
        else:
            self.text = sanitize(data.get("text"))
        self.collectible = bool(data.get("collectible"))
        self.type = HSType[data["type"]]
        self.set  = HSSet[data["set"]]
        self.race = HSRace[data["race"]] if "race" in data else None
        self.school = HSSchool[data["spellSchool"]] if "spellSchool" in data else None
        if self.set == HSSet.CORE or "rarity" not in data:
            self.rarity = None
        else:
            self.rarity = HSRarity[data["rarity"]]
        self.card_class = HSClass[data["cardClass"]] if "cardClass" in data else None
        if "classes" in data:
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

    def to_spoiler(self, columns=79, gutter=1, show_id=False):
        s = ''
        spoiler_fields = list(self.SPOILER_FIELDS)
        if show_id:
            spoiler_fields.insert(0, ("ID", "id"))
        tagwidth = max(len(label) for label, _ in spoiler_fields) + 1
        valwidth = columns - tagwidth - gutter
        for name, attr in spoiler_fields:
            value = getattr(self, attr)
            if value is None or value == '':
                continue
            for i, ln in enumerate(wrap_lines(str(value).strip(), valwidth, 2)):
                tag = '' if i else name + ':'
                s += '{1:{0}}{3:{2}}{4}\n'.format(tagwidth, tag, gutter, '', ln)
        return s

    @property
    def typeline(self):
        subtypes = []
        if self.subtype is not None:
            subtypes.append(self.subtype)
        if self.school is not None:
            subtypes.append(self.school)
        if subtypes:
            return '{} — {}'.format(self.type, ", ".join(map(str, subtypes)))
        else:
            return str(self.type)

    @property
    def subtype(self):
        if self.type is HSType.MINION:
            return self.race
        elif self.type is HSType.SPELL:
            if (self.text or '').startswith('<b>Secret:</b>'):
                return 'Secret'
            elif (self.text or '').startswith('<b>Quest:</b>'):
                return 'Quest'
            elif (self.text or '').startswith('<b>Sidequest:</b>'):
                return 'Sidequest'
            elif (self.text or '').startswith('<b>Questline:</b>'):
                return 'Sidequest'
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
        attribs = []
        if self.rarity is not None:
            attribs.append(str(self.rarity))
        if self.unlock_lvl is not None:
            attribs.append('Unlock: lvl. {}'.format(self.unlock_lvl))
        if self.gold_levels is not None:
            lvls = ', '.join(map(str, self.gold_levels))
            if self.gold_class is not None:
                attribs.append('Gold: {} lvls. {}'.format(self.gold_class,lvls))
            else:
                attribs.append('Gold: lvls. {}'.format(lvls))
        if attribs:
            return '{} ({})'.format(self.set, '; '.join(attribs))
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
    def from_json(cls, cards: [dict], basics=None):
        if basics is None:
            with open(BASIC_JSON) as fp:
                basics = json.load(fp)
        hscards = []
        for c in cards:
            if "type" not in c:
                assert c["id"] == "PlaceholderCard"
                continue
            if c.get("name") in basics:
                c = {**c, **basics[c.get("name")]}
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

def sanitize(txt):
    # Hopefully, Blizzard never releases a card that says "Summon Murloc #1.
    # Collect $200."
    if txt is None:
        return txt
    if txt.startswith('[x]'):
        txt = txt[3:]
    return re.sub(r'[#$](\d+)', r'\1', txt)
