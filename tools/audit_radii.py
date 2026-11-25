"""Check Data/shannon_radii.json against Shannon (1976).

    python tools/audit_radii.py [PATH/TO/periodic_table.json.gz]

The reference is the table of Shannon's effective ionic radii that pymatgen
distributes (pymatgen/core/periodic_table.json.gz, in the pymatgen-core
package; "Shannon radii", "ionic_radius"). With no path, the installed
pymatgen-core is used; tests/data/shannon_1976.json is a copy of just that
table, which the tests use.

Every anion entry (a negative charge) must be one of Shannon's ionic radii
for that ion and coordination number, and every one Shannon gives must be in
the file (#64).

Every cation entry must be, by the rule agreed on #69:
  - one of Shannon's ionic radii for that ion and CN; or
  - recorded under "interpolated" in Data/shannon_radii_sources.json, where
    Shannon does not give that CN: linear in CN between his nearest CNs
    either side, each end one of his radii; or
  - recorded under "derived" there, for an ion Shannon does not list: Gagne's
    measured mean bond length to O at that CN less the O(2-) radius in the
    file, as recorded.

and every CN Shannon lists for a cation the file holds must be in the file,
so that a CN he does not list borrows his nearest. Where he gives several
values at one CN (square-planar, pyramidal, low or high spin), any of them
passes: the rule's preference applies when a value is chosen, and entries
that already held one of his were kept. Exits 1 if any entry breaks the rule. pymatgen labels square-planar and
pyramidal coordinations IVSQ, IIIPY and IVPY; they count as IV and III.
"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'Data' / 'shannon_radii.json'
SOURCES = ROOT / 'Data' / 'shannon_radii_sources.json'
GAGNE = ROOT / 'Data' / 'gagne_bond_lengths.json'
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
         'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIV': 14}


# pymatgen files Shannon's Eu(3+) at CN VII (1.01 A) under a blank charge;
# his table gives it as Eu(3+)
BLANK_CHARGE = {'Eu': '3'}


def reference(path=None, labelled=False):
    """{(element, charge, CN): set of Shannon's ionic radii}; with labelled,
    {(element, charge, CN): [(label, spin, radius)]}."""
    if path is None:
        import pymatgen.core
        path = Path(pymatgen.core.__file__).parent / 'periodic_table.json.gz'
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as fh:
        pt = json.load(fh)
    ref, lab = {}, {}
    for el, d in pt.items():
        sr = d.get('Shannon radii') if isinstance(d, dict) else None
        if not isinstance(sr, dict):
            continue
        for q, cns in sr.items():
            if q == '' and el in BLANK_CHARGE:
                q = BLANK_CHARGE[el]
            if not isinstance(cns, dict) or not q.lstrip('+-').isdigit():
                continue
            for cn, spins in cns.items():
                c = ROMAN.get(cn.upper().replace('SQ', '').replace('PY', ''))
                if c is None or not isinstance(spins, dict):
                    continue
                for sp, v in spins.items():
                    if isinstance(v, dict) and 'ionic_radius' in v:
                        r = round(float(v['ionic_radius']), 3)
                        ref.setdefault((el, int(q), c), set()).add(r)
                        lab.setdefault((el, int(q), c), []).append((cn, sp, r))
    return lab if labelled else ref


def preferred(values):
    """The value #69's rule chooses among several of Shannon's at one CN:
    the plain coordination over square-planar or pyramidal, then high spin
    over low."""
    plain = [x for x in values if x[0].upper() in ROMAN] or values
    high = [x for x in plain if x[1] == 'High Spin'] or plain
    return high[0][2]


def interpolated_ok(ref, el, q, cn, r, rec):
    """The recorded ends are Shannon's, are his nearest CNs either side of
    one he does not give, and the radius is the straight line between them."""
    if rec is None or (el, q, cn) in ref:
        return False
    lo, hi = rec['lo_cn'], rec['hi_cn']
    his = sorted(c for (e, v, c) in ref if e == el and v == q)
    if (lo != max([c for c in his if c < cn], default=None)
            or hi != min([c for c in his if c > cn], default=None)):
        return False
    if (round(rec['lo_radius'], 3) not in ref[(el, q, lo)]
            or round(rec['hi_radius'], 3) not in ref[(el, q, hi)]):
        return False
    line = rec['lo_radius'] + (rec['hi_radius'] - rec['lo_radius']) * (cn - lo) / (hi - lo)
    return abs(float(r) - rec['radius']) < 1e-9 and abs(round(line, 4) - rec['radius']) < 1e-9


def derived_ok(ref, table, gagne, el, q, cn, r, rec):
    """An ion Shannon does not list, from Gagne's mean to O less the file's
    O(2-) radius at the CN recorded."""
    if rec is None or any(e == el and v == q for (e, v, c) in ref):
        return False
    mean = gagne.get(el, {}).get(str(q), {}).get('O', {}).get(str(cn), {}).get('mean')
    o_cns = sorted(int(c) for c in table['O']['-2'])
    nearest = min(o_cns, key=lambda c: (abs(c - cn), c))   # as Eir looks it up
    o = table['O']['-2'].get(str(rec['anion_cn']))
    return (mean is not None and mean == rec['gagne_mean'] and rec['anion_cn'] == nearest
            and o == rec['anion_radius']
            and abs(float(r) - rec['radius']) < 1e-9
            and abs(round(mean - o, 3) - rec['radius']) < 1e-9)


def main(argv):
    ref = reference(argv[1] if len(argv) > 1 else None)
    table = json.loads(TABLE.read_text(encoding='utf-8'))
    src = json.loads(SOURCES.read_text(encoding='utf-8'))
    gagne = json.loads(GAGNE.read_text(encoding='utf-8'))
    fails, cations, counts = [], [], {'Shannon': 0, 'interpolated': 0, 'derived': 0}
    for el, qs in table.items():
        for q, cns in qs.items():
            for cn, r in cns.items():
                k = (el, int(q), int(cn))
                if k in ref and round(float(r), 3) in ref[k]:
                    if k[1] > 0:
                        counts['Shannon'] += 1
                    continue
                if k[1] < 0:
                    fails.append((k, r, sorted(ref.get(k, ()))))
                    continue
                ri = src['interpolated'].get(el, {}).get(q, {}).get(cn)
                rd = src['derived'].get(el, {}).get(q, {}).get(cn)
                if interpolated_ok(ref, *k, r, ri):
                    counts['interpolated'] += 1
                elif derived_ok(ref, table, gagne, *k, r, rd):
                    counts['derived'] += 1
                else:
                    cations.append((k, r, sorted(ref.get(k, ()))))
    missing = []
    # every CN Gagne measured to O for a derived ion is in the file
    for el, qs in src['derived'].items():
        for q in qs:
            for c in gagne.get(el, {}).get(q, {}).get('O', {}):
                if c not in table.get(el, {}).get(q, {}) or c not in qs[q]:
                    missing.append((el, int(q), int(c), 'Gagne measured it'))
    # a value #69 chose (changed, added, an interpolation's ends) is the one
    # its rule prefers among Shannon's at that CN
    lab = reference(argv[1] if len(argv) > 1 else None, labelled=True)
    chosen = [(r['ion'], r['cn'], r['now']) for r in src['changed']]
    chosen += [(r['ion'], r['cn'], r['radius']) for r in src['added']]
    for el, qs in src['interpolated'].items():
        for q, cns in qs.items():
            for rec in cns.values():
                chosen += [(f'{el}{q}+', rec['lo_cn'], rec['lo_radius']),
                           (f'{el}{q}+', rec['hi_cn'], rec['hi_radius'])]
    for ion, c, r in chosen:
        el = ion.rstrip('+').rstrip('0123456789')
        q = int(ion[len(el):].rstrip('+'))
        held = table.get(el, {}).get(str(q), {}).get(str(c))
        want = preferred(lab[(el, q, c)]) if (el, q, c) in lab else None
        if want is None or round(r, 3) != want or held is None or round(held, 3) != want:
            cations.append(((el, q, c), held, [want, 'as #69 prefers; recorded ' + str(r)]))
    for (el, q, c) in sorted(ref):
        if q < 0 and str(c) not in table.get(el, {}).get(str(q), {}):
            fails.append(((el, q, c), None, sorted(ref[(el, q, c)])))
        if q > 0 and str(q) in table.get(el, {}) and str(c) not in table[el][str(q)]:
            missing.append((el, q, c, sorted(ref[(el, q, c)])))
    for k, r, want in fails:
        print(f'ANION  {k[0]}{k[1]:+d} CN {k[2]}: file {r}, Shannon {want or "none"}')
    for k, r, want in sorted(cations):
        print(f'CATION {k[0]}{k[1]:+d} CN {k[2]}: file {r}, Shannon '
              f'{want or "not tabulated"}, and no valid record in {SOURCES.name}')
    for el, q, c, want in missing:
        why = want if isinstance(want, str) else f'Shannon gives {want}'
        print(f'CATION {el}{q:+d} CN {c}: missing from the file ({why})')
    print('anion entries: ' + ('all match Shannon (1976)' if not fails
                               else f'{len(fails)} differ'))
    print(f"cation entries: {counts['Shannon']} Shannon's, {counts['interpolated']} "
          f"interpolated, {counts['derived']} derived"
          + (f'; {len(cations)} break the rule' if cations else ', all by the rule')
          + (f'; {len(missing)} CNs missing' if missing else ''))
    return 1 if fails or cations or missing else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
