import os
import os.path
import click
from   .carddb   import CARDS_URL, CardDB, HSRarity
from   .pdflists import mkpdfcardlist

@click.group(chain=True)
@click.pass_context
def main(ctx):
    ctx.obj = CardDB.from_url(CARDS_URL)

@main.command()
@click.option('-o', '--outfile', type=click.File('w'), default='cards.txt',
              show_default=True)
@click.pass_obj
def spoiler(carddb, outfile):
    COLUMNS = 79
    GUTTER  = 1
    with outfile:
        for card in carddb.cards_sorted():
            print(card.to_spoiler(columns=COLUMNS, gutter=GUTTER), file=outfile)

@main.command()
@click.option('-d', '--output-dir', type=click.Path(file_okay=False),
              default='checklists', show_default=True)
@click.option('-f', '--format', 'chkfmt', type=click.Choice(['txt', 'pdf']),
              default='txt', show_default=True)
@click.pass_obj
def checklists(carddb, output_dir, chkfmt):
    os.makedirs(output_dir, exist_ok=True)
    for hs_set, cards in carddb.by_set():
        outfile = os.path.join(output_dir, hs_set.name + '.' + chkfmt)
        if chkfmt == 'txt':
            with open(outfile, 'w') as fp:
                col_widths = list(map(max, zip(
                    *(map(len, c.checklist_columns())
                      for _,cs in cards for c in cs)
                )))
                print(str(hs_set), file=fp)
                for cls, cs in cards:
                    print(file=fp)
                    print(str(cls).upper(), file=fp)
                    for card in cs:
                        print(
                            '[ ]    ' if card.rarity is HSRarity.LEGENDARY
                                      else '[ ] [ ]',
                            *map(str.ljust,card.checklist_columns(),col_widths),
                            sep='  ',
                            file=fp,
                        )
        elif chkfmt == 'pdf':
            mkpdfcardlist(cards, outfile)
        else:
            assert False, 'invalid checklist format'

if __name__ == '__main__':
    main()
