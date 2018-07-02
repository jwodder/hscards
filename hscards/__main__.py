from pathlib import Path
from .carddb import CARDS_URL, CardDB, HSRarity

def main():
    all_cards = CardDB.from_url(CARDS_URL)

    build_dir = Path('build')
    build_dir.mkdir(exist_ok=True)

    # "Spoiler" list:
    COLUMNS = 79
    GUTTER  = 1
    with open(str(build_dir/'cards.txt'), 'w') as fp:
        for card in all_cards.cards_sorted():
            print(card.to_spoiler(columns=COLUMNS, gutter=GUTTER), file=fp)

    # Checklists:
    chkdir = build_dir/'checklists'
    chkdir.mkdir(exist_ok=True)
    for hs_set, cards in all_cards.by_set():
        col_widths = list(map(max, zip(*(map(len, c.checklist_columns())
                                         for _,cs in cards for c in cs))))
        with open(str(chkdir / (hs_set.name + '.txt')), 'w') as fp:
            print(str(hs_set), file=fp)
            for cls, cs in cards:
                print(file=fp)
                print(str(cls).upper(), file=fp)
                for card in cs:
                    print(
                        '[ ]    ' if card.rarity is HSRarity.LEGENDARY
                                  else '[ ] [ ]',
                        *map(str.ljust, card.checklist_columns(), col_widths),
                        sep='  ',
                        file=fp,
                    )

if __name__ == '__main__':
    main()
