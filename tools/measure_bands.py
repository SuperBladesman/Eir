"""Measure the estimate bands of CELL 2 (#68) from the Data folder.

    python tools/measure_bands.py [--check] [--list]

An expected bond length that Gagne did not measure is estimated, either as
the sum of Shannon radii (tier 4) or by interpolating in valence between two
of Gagne's measured valences of the same ion (tier 5). A band is the 95th
percentile of |estimate - Gagne's mean| / Gagne's mean over the
configurations, bonded to O or N, where both exist. Every estimate is made
by the engine's own functions, exactly as Eir makes it.

The Shannon sums fall into two populations, by whether Shannon gives the
cation's radius at the configuration's CN or Eir borrows it from his nearest
CN; each gets its own band (ESTIMATE_BAND_AT_CN, ESTIMATE_BAND_BORROWED).
Tier 5 is tested by leaving each measured configuration out and
interpolating between the valences either side; its band,
ESTIMATE_BAND_VALENCE, is chosen rather than measured (see CELL 2), so it is
reported but not checked.

--check exits 1 if a measured band, rounded to 0.001, differs from the
engine's constant: re-run this whenever Data/shannon_radii.json or
Data/gagne_bond_lengths.json changes. --list prints every configuration.
"""
import contextlib
import io
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def engine():
    with contextlib.redirect_stdout(io.StringIO()):
        from eir import _engine as e
        e.db_manager.load_shannon_radii()
        e.db_manager.load_bond_lengths()
    return e


def shannon_misses(e):
    """(element, valence, anion, cn, miss, radius at the CN?) for every
    configuration Gagne measured, bonded to O or N, that Shannon covers."""
    out = []
    for (el, v, an, cn), rec in sorted(e.db_manager.bond_lengths.items()):
        if an not in ('O', 'N') or v <= 0:
            continue
        q = e.ALWAYS_ANION.get(an, e.AMPHOTERIC_ANION.get(an))
        r_cat, how = e.get_ionic_radius_fractional(el, v, cn)
        r_an, _ = e.get_ionic_radius_fractional(an, q, cn)
        if r_cat is None or r_an is None:
            continue
        out.append((el, v, an, cn, (r_cat + r_an - rec['mean']) / rec['mean'],
                    how == 'exact'))
    return out


def valence_misses(e):
    """Leave each measured configuration out and interpolate in valence
    between the measured valences either side, each at this CN by tier 1 or
    2, as expected_bond_length does."""
    bl = e.db_manager.bond_lengths
    out = []
    for (el, v, an, cn), rec in sorted(bl.items()):
        if an not in ('O', 'N') or v <= 0:
            continue
        vals = sorted({k[1] for k in bl if k[0] == el and k[2] == an})
        lo = max([x for x in vals if x < v], default=None)
        hi = min([x for x in vals if x > v], default=None)
        if lo is None or hi is None:
            continue
        a = e.expected_bond_length(el, lo, cn, an)
        b = e.expected_bond_length(el, hi, cn, an)
        if not (a and b and a['tier'] <= 2 and b['tier'] <= 2):
            continue
        est = a['mean'] + (v - lo) / (hi - lo) * (b['mean'] - a['mean'])
        out.append((el, v, an, cn, (est - rec['mean']) / rec['mean']))
    return out


def p95(x):
    return float(np.percentile(np.abs(x), 95)) if len(x) else float('nan')


def main(argv):
    e = engine()
    sh = shannon_misses(e)
    vi = valence_misses(e)
    at = np.array([m[4] for m in sh if m[5]])
    bo = np.array([m[4] for m in sh if not m[5]])
    al = np.array([m[4] for m in sh])
    va = np.array([m[4] for m in vi])
    rows = [
        ('Shannon sum, radius at the CN', at, 'ESTIMATE_BAND_AT_CN', True),
        ('Shannon sum, radius borrowed', bo, 'ESTIMATE_BAND_BORROWED', True),
        ('Shannon sum, both together', al, None, False),
        ('valence interpolation', va, 'ESTIMATE_BAND_VALENCE', False),
    ]
    bad = []
    for name, x, const, checked in rows:
        got = p95(x)
        line = (f'{name:32} {len(x):4} configurations  95th percentile '
                f'{100 * got:5.2f}%  median {100 * float(np.median(np.abs(x))):4.2f}%')
        if const:
            have = getattr(e, const)
            line += f'   {const} = {have}'
            if checked and round(got, 3) != round(have, 3):
                line += '  DIFFERS'
                bad.append(const)
            elif not checked:
                line += ' (chosen)'
        print(line)
    if '--list' in argv:
        for el, v, an, cn, m, ok in sh:
            print(f'  Shannon  {el}({v})-{an} CN {cn:2}  {100 * m:+6.1f}%  '
                  f'{"at the CN" if ok else "borrowed"}')
        for el, v, an, cn, m in vi:
            print(f'  valence  {el}({v})-{an} CN {cn:2}  {100 * m:+6.1f}%')
    if '--check' in argv and bad:
        print('Re-measure: ' + ', '.join(bad) + ' no longer match the Data folder.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
