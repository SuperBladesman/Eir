"""Check Data/bvs_parameters.json against its sources.

    python tools/audit_bv_table.py PATH/TO/bvparm2020.cif [PATH/TO/yc5011sup1.txt]

The second file is the text of Chen and Adams (2017), IUCrJ 4, 614,
supporting information (pdftotext -layout yc5011sup1.pdf). With it, every
entry from their softNC1 set is checked against Table S1, and so is the rule
that adds them: a softNC1 pair fitted to at least three environments goes in
where Brown and Gagne have no published row at the anion charge Eir uses,
and no other softNC1 pair does.

Brown's bvparm2020.cif is not part of this repository; it is distributed by
the IUCr (https://www.iucr.org/resources/data/datasets/bond-valence-parameters).
Every entry in the table must match a row of it: same cation, valence and
anion, the anion charge the entry records, its R0 and b, and the reference
code the entry records ('bs' is Gagne and Hawthorne, 2015). The one entry
taken from elsewhere, Fe4+-O from Brown (2009), Table 2, is listed as such.

Each entry must also be the row the merge rule picks: Gagne and Hawthorne
(2015) first, then Brown and Altermatt (1985, 'a'), then Brese and O'Keeffe
(1991, 'b'), then any other published source, then the unpublished ones
(Brown's private communications 'e', Sidey's 'bi', and Hu's 'bq', listed as
'to be published'). Where rows of equal rank differ, the table's choice is
reported, not failed: the 2025 merge did not take them in a fixed order.

Exits 1 if any entry fails.
"""
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'Data' / 'bvs_parameters.json'
# the charge Eir gives each anion (ALWAYS_ANION and AMPHOTERIC_ANION, CELL 1)
EIR_ANION = {'O': -2, 'F': -1, 'Cl': -1, 'Br': -1, 'I': -1, 'S': -2, 'Se': -2,
             'Te': -2, 'N': -3, 'P': -3, 'As': -3, 'H': -1, 'C': -4, 'Si': -4,
             'B': -3}
NOT_IN_BROWN_2020 = {"('Fe', 4, 'O')": 'Brown_2009_Table2_ref54'}


# Sources Brown lists that are not published: his own private communications
# ('e'), Sidey's (2012, 'bi'), and Hu (2014) 'to be published' ('bq', whose
# nitride rows are given per spin state). They rank last.
UNPUBLISHED = {'e', 'bi', 'bq'}
PSEUDO = {'Nx', 'Hx', 'Nh'}


def rank(code, ref):
    if ref == 'Gagne2015':
        return -1
    return 0 if code == 'a' else 1 if code == 'b' else 3 if code in UNPUBLISHED else 2


def read_softnc1(path):
    """Table S1 rows: {(M, vM, X): (vX, n, b, R0_softNC1)}."""
    num = r'-?\d+(?:\.\d+)?'
    pat = re.compile(rf'^\s*([A-Z][a-z]?)\s+(-?\d+)\s+([A-Z][a-z]?)\s+(-?\d+)\s+(\d+)\s+'
                     rf'({num})' + rf'\s+({num})' * 11 + r'\s*$')
    out, live = {}, False
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if 'Table S1' in line:
            live = True
        if 'Table S2' in line:
            live = False
        m = pat.match(line) if live else None
        if m:
            g = m.groups()
            out[(g[0], int(g[1]), g[2])] = (int(g[3]), int(g[4]), float(g[5]), float(g[10]))
    return out


def main(bvparm, softnc1=None):
    lines = Path(bvparm).read_text(encoding='latin-1').splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.strip() == '_valence_param_details') + 1
    rows = defaultdict(list)
    for l in lines[start:]:
        t = l.split()
        if len(t) >= 7 and re.match(r'^-?\d+$', t[1]) and re.match(r'^-?\d+$', t[3]):
            try:
                rows[(t[0], int(t[1]), t[2])].append(
                    (int(t[3]), float(t[4]), float(t[5]), t[6]))
            except ValueError:
                pass
    table = json.loads(TABLE.read_text())
    bad, ties = [], []
    soft = read_softnc1(softnc1) if softnc1 else None
    if soft is not None:
        for (m, vm, x), (vx, n, b, r0) in soft.items():
            # pseudo-atoms: N of a cyanide (Nx), H as X-rays place it (Hx),
            # ammonium with H unresolved (Nh)
            if m == x or m in PSEUDO or x in PSEUDO or vx != EIR_ANION.get(x) or n < 3:
                continue
            published = [r for r in rows.get((m, vm, x), [])
                         if r[0] == vx and r[3] not in UNPUBLISHED]
            k = str((m, vm, x))
            if not published and table.get(k, {}).get('reference') != 'ChenAdams2017_softNC1':
                bad.append((k, f'softNC1 ({n} environments) should fill this pair'))
    for k, e in table.items():
        key = ast.literal_eval(k)
        if e.get('reference') == 'ChenAdams2017_softNC1':
            if soft is None:
                continue
            got = soft.get(key)
            if got is None or got[0] != e.get('anion_charge') or abs(got[2] - e['b']) > 1e-9 \
                    or abs(got[3] - e['r0']) > 1e-9 or got[1] != e.get('n_environments') or got[1] < 3:
                bad.append((k, f'does not match Table S1: {got}'))
            elif any(r[0] == got[0] and r[3] not in UNPUBLISHED for r in rows.get(key, [])):
                bad.append((k, 'a published Brown or Gagne row exists; softNC1 should not be used'))
            continue
        if k in NOT_IN_BROWN_2020:
            if e.get('reference') != NOT_IN_BROWN_2020[k]:
                bad.append((k, 'expected reference ' + NOT_IN_BROWN_2020[k]))
            continue
        q, code = e.get('anion_charge'), e.get('brown_code')
        if q is None or q != EIR_ANION.get(key[2]):
            bad.append((k, f'anion_charge {q}, Eir gives {key[2]} {EIR_ANION.get(key[2])}'))
            continue
        here = [r for r in rows.get(key, []) if r[0] == q]
        hit = [r for r in here if r[3] == code and abs(r[1] - e['r0']) < 1e-6
               and abs(r[2] - e['b']) < 1e-6]
        if not hit:
            bad.append((k, f"no {code!r} row at {q:+d} with R0 {e['r0']}, b {e['b']}"))
            continue
        want = (e['reference'] == 'Gagne2015') == (code == 'bs')
        if not want:
            bad.append((k, f"reference {e['reference']!r} with code {code!r}"))
            continue
        if e['reference'] == 'Gagne2015':
            continue
        if any(r[3] == 'bs' for r in here):
            bad.append((k, 'Gagne and Hawthorne (2015) give this pair; the table does not use it'))
            continue
        others = [r for r in here if r[3] != 'bs']
        best = min(rank(r[3], '') for r in others)
        if rank(code, '') != best:
            bad.append((k, f'merge rule picks rank {best}, table has {code!r}'))
        elif len({(r[1], r[2]) for r in others if rank(r[3], '') == best}) > 1:
            ties.append((k, code, [(r[1], r[2], r[3]) for r in others
                                   if rank(r[3], '') == best]))
    print(f'{len(table)} entries; {len(bad)} fail; {len(ties)} equal-rank choices')
    for k, why in bad:
        print('  FAIL', k, why)
    for k, code, opts in ties:
        print('  tie ', k, 'takes', code, 'of', opts)
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
