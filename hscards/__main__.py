import json
import os
import os.path
import click
import requests
from   .carddb   import CARDS_URL, CardDB, HSRarity
from   .pdflists import mkpdfcardlist

def json_source(src):
    if src.lower().startswith(('http://', 'https://')):
        r = requests.get(src)
        r.raise_for_status()
        return r.json()
    else:
        with click.open_file(src) as fp:
            return json.load(fp)

@click.group('hscards', chain=True)
@click.option('-c', '--cards-file', type=json_source, default=CARDS_URL,
              help='Source of card data', show_default=True, metavar='FILE|URL')
@click.pass_context
def main(ctx, cards_file):
    """ Generate Hearthstone card spoilers & checklists """
    ctx.obj = CardDB.from_json(cards_file)

@main.command()
@click.option('-I', '--show-ids', is_flag=True, help='Include card IDs')
@click.option('-o', '--outfile', type=click.File('w'), default='cards.txt',
              show_default=True, help='Name of output file')
@click.pass_obj
def spoiler(carddb, outfile, show_ids):
    """ Generate text spoiler """
    COLUMNS = 79
    GUTTER  = 1
    with outfile:
        for card in carddb.cards_sorted():
            print(card.to_spoiler(
                columns = COLUMNS,
                gutter  = GUTTER,
                show_id = show_ids,
            ), file=outfile)

@main.command()
@click.option('-d', '--output-dir', type=click.Path(file_okay=False),
              default='checklists', show_default=True,
              help='Name of output directory')
@click.option('-f', '--format', 'chkfmt', type=click.Choice(['txt', 'pdf']),
              default='txt', show_default=True, help='Set checklist format')
@click.pass_obj
def checklists(carddb, output_dir, chkfmt):
    """ Generate card set checklists """
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
    main(prog_name=__package__)
