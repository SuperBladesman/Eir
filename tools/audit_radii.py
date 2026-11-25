"""Check the anion entries of Data/shannon_radii.json against Shannon (1976).

    python tools/audit_radii.py [PATH/TO/periodic_table.json.gz]

The reference is the table of Shannon's effective ionic radii that pymatgen
distributes (pymatgen/core/periodic_table.json.gz, in the pymatgen-core
package; "Shannon radii", "ionic_radius"). With no path, the installed
pymatgen-core is used.

Every anion entry (a negative charge) must be one of Shannon's ionic radii
for that ion and coordination number, and every one Shannon gives must be in
the file. Exits 1 if any differs. Cation entries are compared and listed but
do not fail the check: they are reviewed separately (#64).
"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'Data' / 'shannon_radii.json'
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
         'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIV': 14}


def reference(path=None):
    if path is None:
        import pymatgen.core
        path = Path(pymatgen.core.__file__).parent / 'periodic_table.json.gz'
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as fh:
        pt = json.load(fh)
    ref = {}
    for el, d in pt.items():
        sr = d.get('Shannon radii') if isinstance(d, dict) else None
        if not isinstance(sr, dict):
            continue
        for q, cns in sr.items():
            if not isinstance(cns, dict) or not q.lstrip('+-').isdigit():
                continue
            for cn, spins in cns.items():
                c = ROMAN.get(cn.replace('sq', '').replace('py', ''))
                if c is None or not isinstance(spins, dict):
                    continue
                for v in spins.values():
                    if isinstance(v, dict) and 'ionic_radius' in v:
                        ref.setdefault((el, int(q), c), set()).add(
                            round(float(v['ionic_radius']), 3))
    return ref


def main(argv):
    ref = reference(argv[1] if len(argv) > 1 else None)
    table = json.loads(TABLE.read_text(encoding='utf-8'))
    fails, cations = [], []
    for el, qs in table.items():
        for q, cns in qs.items():
            for cn, r in cns.items():
                k = (el, int(q), int(cn))
                ok = k in ref and round(float(r), 3) in ref[k]
                if not ok:
                    (fails if k[1] < 0 else cations).append(
                        (k, r, sorted(ref.get(k, ()))))
    for (el, q, c) in sorted(ref):
        if q < 0 and str(c) not in table.get(el, {}).get(str(q), {}):
            fails.append(((el, q, c), None, sorted(ref[(el, q, c)])))
    for k, r, want in fails:
        print(f'ANION  {k[0]}{k[1]:+d} CN {k[2]}: file {r}, Shannon {want or "none"}')
    print(f'{len(cations)} cation entries differ from Shannon or are not in '
          f'his table; reviewed separately.')
    print('anion entries: ' + ('all match Shannon (1976)' if not fails
                               else f'{len(fails)} differ'))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
