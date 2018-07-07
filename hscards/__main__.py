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

@click.group()
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
@click.argument('cardsets', nargs=-1)
@click.pass_obj
def checklists(carddb, output_dir, chkfmt, cardsets):
    """ Generate card set checklists """
    os.makedirs(output_dir, exist_ok=True)
    mkcardlist = mktxtcardlist if chkfmt == 'txt' else mkpdfcardlist
    cards_by_set = {
        hs_set.name: (hs_set, cards) for (hs_set, cards) in carddb.by_set()
    }
    if cardsets:
        for c in cardsets:
            if c in cards_by_set:
                hs_set, cards = cards_by_set[c]
                outfile = os.path.join(output_dir, hs_set.name + '.' + chkfmt)
                mkcardlist(hs_set, cards, outfile)
            else:
                click.echo('{}: unknown set'.format(c), err=True)
    else:
        for hs_set, cards in cards_by_set.values():
            outfile = os.path.join(output_dir, hs_set.name + '.' + chkfmt)
            mkcardlist(hs_set, cards, outfile)

def mktxtcardlist(hs_set, cards, outfile):
    with open(outfile, 'w') as fp:
        col_widths = list(map(max, zip(
            *(map(len, c.checklist_columns()) for _,cs in cards for c in cs)
        )))
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
    main(prog_name=__package__)
