"""Build the two figures of the JOSS paper.

    python paper/make_figures.py facets
    python paper/make_figures.py report PATH/TO/ICSD_85235.cif

`facets` draws facets.svg and facets.png: the order in which Eir assesses a
structure. Every box in a column has the same width and every label the same
offset, so nothing depends on a layout engine.

`report` runs `eir check` on the CIF (ICSD files are licensed, so the CIF is
not in this repository) and writes report_85235.png: the top of the report and
its site table, with the index table, geometry screens, anion line and
provenance hidden, beside the CrO6 octahedron from the same report.
Needs Playwright with Chromium, and Pillow.
"""
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
INK, MUTED, LINE = '#17212b', '#4a5866', '#17212b'
OUTCOME = {  # fill, border, title colour
    'EXPUNGE': ('#f9e0de', '#b0271f', '#8f1d17'),
    'NOT_ASSESSED': ('#eaedf0', '#586776', '#3d4a57'),
    'FLAG': ('#fcebd0', '#9a5800', '#7a4600'),
    'ACCEPT': ('#dcefe0', '#2c6b3f', '#1f5230'),
}

# main column: (badge, title, description lines, outcome or None, outcome text)
STEPS = [
    (None, 'CIF', [], None, None),
    (None, 'Reading stage', ['Repairs made by feature and recorded;',
                             'every bond computed from the positions.'], None, None),
    ('P', 'Parse', ['Can the file be read?'],
     'EXPUNGE', ['No bond valence result quoted.']),
    ('G', 'Geometry', ['Can the atoms be where the file puts them?',
                       'Six independent screens; a proposed origin',
                       'shift is tested on a copy, never applied.'],
     'EXPUNGE', ['No bond valence result quoted.']),
    ('R', 'Reference', ['Are there bond valence parameters and',
                        'measured bond lengths for every ion?'],
     'NOT_ASSESSED', ['Part of the analysis missing, not wrong.']),
    ('M', 'Model', ['Is the deposited description unambiguous?'],
     'FLAG', ['Sums and GII hold; ambiguity named.']),
]
FINAL = ('ACCEPT', ['Or ACCEPT_IMPRECISE, ACCEPT_HOMOVALENT or',
                    'ACCEPT_HETEROVALENT; sums and GII reported.'])


def facets():
    W, X0, MW, OX, OW = 800, 24, 380, 484, 292   # page, main x, main width, outcome x, width
    PAD, T, D, LH, GAP = 16, 15, 12.5, 17.5, 34  # padding, font sizes, line height, gap
    out, y = [], 16

    def box(x, y, w, h, fill, stroke, sw=1.4, r=10):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(x, y, s, size, weight=400, fill=INK, anchor='start'):
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                   f'fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')

    def arrow(x1, y1, x2, y2):
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" '
                   f'stroke-width="1.4" marker-end="url(#a)"/>')

    def height(lines):
        return 2 * PAD + T + (LH * len(lines) + 4 if lines else 0) - 4

    cx = X0 + MW / 2
    for i, (badge, title, lines, outcome, otext) in enumerate(STEPS):
        h = 44 if title == 'CIF' else height(lines)
        if title == 'CIF':
            box(X0, y, MW, h, '#eef1f4', '#586776', r=6)
            text(X0 + PAD, y + h / 2 + 5, 'CIF file', T, 700)
        else:
            box(X0, y, MW, h, 'white', INK)
            tx = X0 + PAD
            if badge:
                out.append(f'<rect x="{tx}" y="{y + PAD - 2}" width="20" height="20" '
                           f'rx="4" fill="{INK}"/>')
                text(tx + 10, y + PAD + 13, badge, 13, 700, 'white', 'middle')
                tx += 30
            text(tx, y + PAD + 13, title, T, 700)
            for k, ln in enumerate(lines):
                text(X0 + PAD, y + PAD + T + 8 + LH * (k + 1) - 4, ln, D, 400, MUTED)
        if outcome:
            oh = height(otext)
            oy = y + (h - oh) / 2
            fill, stroke, tcol = OUTCOME[outcome]
            box(OX, oy, OW, oh, fill, stroke)
            text(OX + PAD, oy + PAD + 13, outcome, T, 700, tcol)
            for k, ln in enumerate(otext):
                text(OX + PAD, oy + PAD + T + 8 + LH * (k + 1) - 4, ln, D, 400, MUTED)
            arrow(X0 + MW, y + h / 2, OX - 2, y + h / 2)
            text((X0 + MW + OX) / 2, y + h / 2 - 7, 'fails', 12, 500, MUTED, 'middle')
        y += h
        arrow(cx, y, cx, y + GAP - 2)
        if badge:
            text(cx + 8, y + GAP / 2 + 4, 'passes', 12, 500, MUTED)
        y += GAP
    outcome, otext = FINAL
    h = height(otext)
    fill, stroke, tcol = OUTCOME[outcome]
    box(X0, y, MW, h, fill, stroke)
    text(X0 + PAD, y + PAD + 13, outcome, T, 700, tcol)
    for k, ln in enumerate(otext):
        text(X0 + PAD, y + PAD + T + 8 + LH * (k + 1) - 4, ln, D, 400, MUTED)
    H = int(round(y + h + 16))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="Inter, Helvetica, Arial, sans-serif">'
           f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
           f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
           f'fill="{LINE}"/></marker></defs><rect width="{W}" height="{H}" fill="white"/>'
           + ''.join(out) + '</svg>')
    (HERE / 'facets.svg').write_text(svg, encoding='utf-8')
    shoot_svg(HERE / 'facets.svg', HERE / 'facets.png', W, H)


def shoot_svg(svg, png, w, h):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=3)
        pg.goto(svg.as_uri())
        pg.screenshot(path=str(png), clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        b.close()


HIDE = """
section.quote.withheld table.indices, section.quote.withheld p.small.muted,
.page > section:nth-of-type(3), .page > section:nth-of-type(4) p.small.muted:first-of-type,
.page > section:nth-of-type(5), .page > section:nth-of-type(6), section.prov, footer
  { display: none !important; }
.page { max-width: 960px !important; } div.scroll { overflow: visible !important; }
table.sites th, table.sites td { white-space: nowrap; vertical-align: middle; }
sup { line-height: 0; }
"""


def report(cif):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    work = Path(tempfile.mkdtemp())
    src = work / Path(cif).name
    src.write_bytes(Path(cif).read_bytes())
    html = work / 'report.html'
    subprocess.run(['eir', 'check', str(src), '--report', str(html)], check=True,
                   stdout=subprocess.DEVNULL)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2)
        pg.goto(html.as_uri())
        pg.wait_for_timeout(600)
        pg.add_style_tag(content='sup { line-height: 0; } div.polys figure { width: 330px !important; max-width: none !important; } div.polys figure:not(:last-child) { display: none !important; }')
        figs = pg.query_selector_all('div.polys figure')
        figs[-1].screenshot(path=str(work / 'b.png'))
        pg.add_style_tag(content=HIDE)
        pg.wait_for_timeout(300)
        top = pg.query_selector('section.verdict').bounding_box()['y']
        sites = pg.query_selector('.page > section:nth-of-type(4)').bounding_box()
        pg.screenshot(path=str(work / 'a.png'),
                      clip={'x': 0, 'y': 0, 'width': 1000, 'height': sites['y'] + sites['height'] + 16})
        b.close()
    a, c = Image.open(work / 'a.png'), Image.open(work / 'b.png')
    gap = 48
    canvas = Image.new('RGB', (a.width + gap + c.width + 40, max(a.height, int(top * 2) + c.height)), 'white')
    canvas.paste(a, (0, 0))
    canvas.paste(c, (a.width + gap, int(top * 2)))   # card top level with the verdict box
    canvas.save(HERE / 'report_85235.png')


if __name__ == '__main__':
    if sys.argv[1:2] == ['facets']:
        facets()
    elif sys.argv[1:2] == ['report'] and len(sys.argv) == 3:
        report(sys.argv[2])
    else:
        sys.exit(__doc__)
