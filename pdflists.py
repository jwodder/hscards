#!/usr/bin/env python3
from   math                    import cos, sin, tan, tau
from   pathlib                 import Path
from   reportlab.lib           import pagesizes
from   reportlab.lib.units     import inch
from   reportlab.pdfgen.canvas import Canvas
from   hscards                 import CARDS_URL, CardDB, HSRarity

FONT_NAME = 'Times-Roman'
FONT_SIZE = 10
CAP_SIZE  = 12
SC_SIZE   = 10

CARDS_PER_CLASS = 15

LINE_HEIGHT  = 12
BLOCK_HEIGHT = LINE_HEIGHT * (CARDS_PER_CLASS + 1)
GUTTER       = LINE_HEIGHT / 2
BUBBLE_SIZE  = 9
BUBBLE_RAD   = 3
STAR_RAD     = 4
LITTLE_RAD   = 2 * STAR_RAD * cos(0.15 * tau) / tan(tau/5)
BUBBLE_START = -4 * BUBBLE_SIZE - GUTTER

RARITY_COLORS = {
    None: (0, 0, 0),
    HSRarity.FREE: (0, 0, 0),
    HSRarity.COMMON: (0, 0, 0),
    HSRarity.RARE: (0, 0, 1),
    HSRarity.EPIC: (0.5, 0, 0.5),
    HSRarity.LEGENDARY: (1, 0.5, 0),
}

def main():
    chkdir = Path('build', 'checklists')
    chkdir.mkdir(exist_ok=True)
    all_cards = CardDB.from_url(CARDS_URL)
    for hs_set, cards in all_cards.by_set():
        mkpdfcardlist(cards, str(chkdir / (hs_set.name + '.pdf')))

def mkpdfcardlist(cards, outpath):
    def start_class(cls_name):
        nonlocal alt_side, begun, y
        if begun:
            if y <= bottom_margin + BLOCK_HEIGHT:
                if alt_side:
                    alt_side = False
                    c.showPage()
                    c.setFont(FONT_NAME, FONT_SIZE)
                    c.translate(left_margin, 0)
                else:
                    alt_side = True
                    c.translate(block_shift, 0)
                y = top_margin
            else:
                y -= LINE_HEIGHT
        else:
            begun = True
        y -= LINE_HEIGHT
        c.setStrokeColorRGB(0,0,0)
        c.setFillColorRGB(0,0,0)
        c.setFontSize(CAP_SIZE)
        c.drawString(0, y, cls_name[0])
        x = c.stringWidth(cls_name[0])
        c.setFontSize(SC_SIZE)
        c.drawString(x, y, cls_name[1:])
        c.setFontSize(FONT_SIZE)
        c.line(
            BUBBLE_START,
            y - LINE_HEIGHT + FONT_SIZE,
            BUBBLE_START + block_width,
            y - LINE_HEIGHT + FONT_SIZE,
        )

    def show_card(card):
        nonlocal alt_side, y
        if y <= bottom_margin + LINE_HEIGHT:
            if alt_side:
                alt_side = False
                c.showPage()
                c.setFont(FONT_NAME, FONT_SIZE)
                c.translate(left_margin, 0)
            else:
                alt_side = True
                c.translate(block_shift, 0)
            y = top_margin
        else:
            y -= LINE_HEIGHT
        c.setStrokeColorRGB(*RARITY_COLORS[card.rarity])
        c.setFillColorRGB(*RARITY_COLORS[card.rarity])
        x = BUBBLE_START
        circle(c, x, y)
        x += BUBBLE_SIZE
        if card.rarity is not HSRarity.LEGENDARY:
            circle(c, x, y)
        x += BUBBLE_SIZE
        star(c, x, y)
        x += BUBBLE_SIZE
        if card.rarity is not HSRarity.LEGENDARY:
            star(c, x, y)
        c.drawString(0, y, card.name)
        c.drawRightString(cost_end, y, str(card.cost))
        c.drawString(type_start, y, str(card.typeline))
        if card.statline:
            c.drawAlignedString(slash_point, y, card.statline, pivotChar='/')

    c = Canvas(outpath, pagesizes.letter)
    c.setFont(FONT_NAME, FONT_SIZE)
    namelen = max(c.stringWidth(card.name) for _,cs in cards for card in cs)
    typelen = max(c.stringWidth(card.typeline) for _,cs in cards for card in cs)
    tens = c.stringWidth('88')
    cost_end = namelen + GUTTER + tens
    type_start = cost_end + GUTTER
    slash_point = type_start + typelen + GUTTER + tens
    block_width = slash_point + c.stringWidth('/') + tens - BUBBLE_START
    block_shift = block_width + 2 * GUTTER
    left_margin = (8.5 * inch - block_width - block_shift)/2 - BUBBLE_START
    c.translate(left_margin, 0)
    bottom_margin = (11 * inch - 3 * (BLOCK_HEIGHT + LINE_HEIGHT)) / 2
    top_margin = 11 * inch - bottom_margin
    y = top_margin
    begun = False
    alt_side = False
    for cls, cs in cards:
        start_class(str(cls).upper())
        for card in cs:
            show_card(card)
    c.showPage()
    c.save()

def circle(c, x, y):
    c.saveState()
    c.setLineWidth(0.5)
    c.circle(x + BUBBLE_SIZE/2, y + LINE_HEIGHT/2 - FONT_SIZE/3, BUBBLE_RAD)
    c.restoreState()

def star(c, x, y):
    c.saveState()
    c.setLineWidth(0.5)
    c.translate(x + BUBBLE_SIZE/2, y + LINE_HEIGHT/2 - FONT_SIZE/3)
    p = c.beginPath()
    p.moveTo(0, STAR_RAD)
    θ = tau/4
    for r in [LITTLE_RAD, STAR_RAD] * 4 + [LITTLE_RAD]:
        θ += tau/10
        p.lineTo(r*cos(θ), r*sin(θ))
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

if __name__ == '__main__':
    main()
