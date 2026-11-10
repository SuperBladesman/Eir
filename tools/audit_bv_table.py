"""Check Data/bvs_parameters.json against Brown's compilation.

    python tools/audit_bv_table.py PATH/TO/bvparm2020.cif

Brown's bvparm2020.cif is not part of this repository; it is distributed by
the IUCr (https://www.iucr.org/resources/data/datasets/bond-valence-parameters).
Every entry in the table must match a row of it: same cation, valence and
anion, the anion charge the entry records, its R0 and b, and the reference
code the entry records ('bs' is Gagne and Hawthorne, 2015). The one entry
taken from elsewhere, Fe4+-O from Brown (2009), Table 2, is listed as such.

Each entry must also be the row the merge rule picks: Gagne and Hawthorne
(2015) first, then Brown and Altermatt (1985, 'a'), then Brese and O'Keeffe
(1991, 'b'), then any other published source, then Brown's private
communications ('e'). Where rows of equal rank differ, the table's choice is
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


def rank(code, ref):
    if ref == 'Gagne2015':
        return -1
    return 0 if code == 'a' else 1 if code == 'b' else 3 if code == 'e' else 2


def main(bvparm):
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
    for k, e in table.items():
        key = ast.literal_eval(k)
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
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
