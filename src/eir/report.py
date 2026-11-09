"""The one-structure report: one CIF in, one self-contained HTML page out.

The page reads the engine's own columns and draws the coordination polyhedra
from the same symmetry expansion the bond valence sums use. Nothing on it is
recomputed: where a number appears, it is a column in the per-site or
per-structure table, and the column is named.
"""

import base64
import datetime as _dt
import hashlib
import html
import io
import math
import re

from . import __version__
from .explain import FACETS, INDEX_NAMES, explain, pretty

ESC = html.escape


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _num(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _bool(x):
    if x is None:
        return None
    s = str(x).strip().lower()
    if s == 'true':
        return True
    if s == 'false':
        return False
    return None


def _str(x):
    if x is None:
        return None
    try:
        if x != x:
            return None
    except Exception:
        pass
    s = str(x).strip()
    return s or None


def _f(x, nd=3):
    v = _num(x)
    return '–' if v is None else f'{v:.{nd}f}'


def _sv(result, col):
    """A structure-level value: the structure row, else the first site row
    that carries it (some structure-level columns live only in the site
    table)."""
    st = result.structure
    if st is not None and col in st.index:
        v = st.get(col)
        if _str(v) is not None:
            return v
    s = result.sites
    if s is not None and col in s.columns:
        vals = s[col].dropna()
        if len(vals):
            return vals.iloc[0]
    return None


def formula_html(f):
    f = _str(f)
    if not f:
        return ''
    out = []
    for tok in f.split():
        m = re.match(r'^([A-Z][a-z]?)([\d.]*)$', tok)
        if not m:
            out.append(ESC(tok))
            continue
        el, n = m.groups()
        out.append(ESC(el) + (f'<sub>{ESC(n)}</sub>' if n and n != '1' else ''))
    return ''.join(out)


def spacegroup_html(sg):
    sg = _str(sg)
    if not sg:
        return ''
    toks = sg.split()
    setting = None
    if len(toks) > 1 and toks[-1] in ('Z', 'S', 'H', 'R'):
        setting = toks.pop()
    parts = []
    for i, t in enumerate(toks):
        m = re.match(r'^(-?)(\d)(\d?)(/[a-z]+)?$', t)
        if m:
            bar, ax, screw, rest = m.groups()
            s = (f'<span class="bar">{ax}</span>' if bar else ax)
            s += f'<sub>{screw}</sub>' if screw else ''
            if rest:
                s += '/<i>' + ESC(rest[1:]) + '</i>'
            parts.append(s)
        elif re.match(r'^[A-Za-z]+$', t):
            parts.append(f'<i>{ESC(t)}</i>')
        else:
            parts.append(ESC(t))
    out = ''.join(parts)
    if setting:
        label = {'Z': 'origin choice 2', 'S': 'origin choice 1',
                 'H': 'hexagonal axes', 'R': 'rhombohedral axes'}[setting]
        out += f' <span class="muted">({label})</span>'
    return out


def ion_html(el, v):
    el = _str(el) or '?'
    v = _num(v)
    if v is None:
        return ESC(el)
    sign = '+' if v > 0 else '−'
    mag = f'{abs(v):g}'
    return f'{ESC(el)}<sup>{"" if mag == "1" else mag}{sign}</sup>'


# ---------------------------------------------------------------------------
# polyhedra
# ---------------------------------------------------------------------------
def _positions(sites):
    """One row per crystallographic position: the dominant species, plus the
    occupancy string for a shared position."""
    if sites is None or not len(sites):
        return []
    rows = []
    key = 'coords' if 'coords' in sites.columns else 'site_label'
    for _, grp in sites.groupby(key, sort=False):
        g = grp
        if 'is_dominant_species' in g.columns:
            dom = g[g['is_dominant_species'].astype(str).str.lower() == 'true']
            if len(dom):
                g = dom
        if 'occupancy' in g.columns:
            g = g.sort_values('occupancy', ascending=False)
        rows.append((g.iloc[0], grp))
    return rows


def _engine():
    from . import _engine as e
    return e


def _draw_polyhedron(cif_path, row, highlight=None):
    """PNG bytes of one coordination polyhedron, or None."""
    e = _engine()
    el, lab = _str(row.get('element')), _str(row.get('site_label'))
    cn = int(_num(row.get('cn')) or 0)
    try:
        centre, ligs = e._viz_local_environment(str(cif_path), el, lab)
    except Exception:
        return None, []
    if centre is None or not ligs or cn <= 0:
        return None, []
    ligs = ligs[:cn]
    import numpy as np
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    c = np.asarray(centre, float)
    P = np.array([np.asarray(p, float) - c for _, p, _ in ligs])
    d = np.array([dd for _, _, dd in ligs])
    lig_el = [x for x, _, _ in ligs]
    colours = getattr(e, 'VIZ_ELEMENT_COLOURS', {})
    default = getattr(e, 'VIZ_DEFAULT_COLOUR', '#c0c0c0')
    ccol = colours.get(el, default)

    fig = Figure(figsize=(2.3, 2.3), dpi=160, layout='none')
    FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    ax.set_proj_type('ortho')
    ax.view_init(elev=17, azim=-58)

    # faces of the polyhedron, where there is one to draw
    if len(P) >= 4:
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(P)
            faces = [P[s] for s in hull.simplices]
            pc = Poly3DCollection(faces, facecolor=ccol, alpha=0.22,
                                  edgecolor='#555555', linewidth=0.35)
            ax.add_collection3d(pc)
        except Exception:
            pass

    short = int(np.argmin(d))
    for i, p in enumerate(P):
        hot = highlight == 'shortest_bond' and i == short
        ax.plot([0, p[0]], [0, p[1]], [0, p[2]],
                color='#E7004C' if hot else '#444444',
                linewidth=2.2 if hot else 0.9, zorder=3)
    if highlight == 'anion_pair' and len(P) >= 2:
        best, pair = None, None
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                dd = float(np.linalg.norm(P[i] - P[j]))
                if best is None or dd < best:
                    best, pair = dd, (i, j)
        floor = getattr(e, 'ANION_ANION_MIN', 2.35)
        if pair and best < floor:
            a, b = P[pair[0]], P[pair[1]]
            ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]],
                    color='#E7004C', linewidth=2.4, zorder=4)
    ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=70,
               c=[colours.get(x, default) for x in lig_el],
               edgecolors='#333333', linewidths=0.4, depthshade=False,
               zorder=5)
    ax.scatter([0], [0], [0], s=140, c=[ccol], edgecolors='#222222',
               linewidths=0.6, depthshade=False, zorder=6)
    r = float(max(np.abs(P).max(), 1.0)) * 1.08
    for setlim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        setlim(-r, r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True)
    return buf.getvalue(), list(zip(lig_el, d))


def _bond_summary(el, pairs):
    """'4 x 1.751 A' style, grouped to 0.001 A."""
    groups = {}
    for lel, dd in pairs:
        k = (lel, round(float(dd), 3))
        groups[k] = groups.get(k, 0) + 1
    parts = [f'{n}× {d:.3f}' for (_, d), n in sorted(groups.items(),
                                                          key=lambda t: t[0][1])]
    ligs = sorted({l for l, _ in pairs})
    return f'{ESC(el)}–{"/".join(ESC(l) for l in ligs)}: ' + ', '.join(parts) + ' Å'


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------
TIER_CLASS = {'ACCEPT': 'ok', 'ACCEPT_IMPRECISE': 'ok', 'ACCEPT_HOMOVALENT': 'ok',
              'ACCEPT_HETEROVALENT': 'ok', 'FLAG': 'warn',
              'NOT_ASSESSED': 'na', 'EXPUNGE': 'bad'}

STATE_TEXT = {'pass': 'passed', 'fail': 'failed', 'caveat': 'caveat',
              'not reached': 'not reached'}


def _verdict_section(result, x):
    cls = TIER_CLASS.get(x['tier'], 'na')
    facets = ''.join(
        f'<li class="facet {x["facets"].get(f, "none").replace(" ", "-")}">'
        f'<span class="fl">{f}</span><span class="fn">{ESC(name)}</span>'
        f'<span class="fs">{ESC(STATE_TEXT.get(x["facets"].get(f), ""))}</span>'
        f'</li>'
        for f, name, _ in FACETS) if x['facets'] else ''
    rows = []
    if x['reason']:
        rows.append(f'<p class="reason">{ESC(x["reason"])}</p>')
    if x['evidence']:
        rows.append('<dl class="kv"><dt>Evidence</dt>'
                    f'<dd class="mono">{ESC(x["evidence"])}</dd>')
        if x['code'] not in (None, '-', 'P'):
            rows.append(f'<dt>Code</dt><dd><span class="mono">{ESC(x["code"])}'
                        f'</span> <span class="muted">{ESC(x["reason_key"] or "")}'
                        f'</span></dd>')
        rows.append('</dl>')
    if x.get('screen_note'):
        rows.append(f'<p class="caution">{ESC(x["screen_note"])}</p>')
    return f'''
<section class="verdict {cls}">
  <div class="tierline"><span class="tier">{ESC(x["tier"] or "")}</span>
  <h2>{ESC(x["headline"])}</h2></div>
  <p class="meaning">{ESC(x["meaning"])}</p>
  {''.join(rows)}
  {f'<ol class="facets" aria-label="The four integrity facets">{facets}</ol>' if facets else ''}
</section>'''


def _quote_section(result, x):
    q = x['quote']
    if not q:
        return ''
    title = {'quote': 'The number to quote', 'caveat': 'The number, with a caveat',
             'partial': 'Bond valence result, unverified',
             'withheld': 'Bond valence result, withheld'}[q['status']]
    if q['number'] is None:
        return (f'<section class="quote withheld"><h3>{title}</h3>'
                f'<p>{ESC(q["note"])}</p></section>')
    rec = _str(_sv(result, 'gii_recommended'))
    rows = []
    for k in ('gii', 'wagii', 'gii_site_averaged'):
        v = _num(_sv(result, k))
        if v is None:
            continue
        sg = _num(_sv(result, f'{k}_sigma'))
        short, long_ = INDEX_NAMES[k]
        mark = ' class="rec"' if k == rec else ''
        rows.append(
            f'<tr{mark}><td>{ESC(short)}</td><td class="n">{v:.3f}</td>'
            f'<td class="n">{"" if sg is None else f"± {sg:.3f}"}</td>'
            f'<td class="muted">{ESC(long_)}'
            f'{" — recommended for this structure" if k == rec else ""}'
            f'</td></tr>')
    table = ('<table class="indices"><thead><tr><th>Index</th><th>v.u.</th>'
             '<th>σ</th><th></th></tr></thead><tbody>'
             + ''.join(rows) + '</tbody></table>') if rows else ''
    return f'''
<section class="quote {q["status"]}">
  <h3>{title}</h3>
  <p class="big"><span class="idx">{ESC(q["short"])}</span>
     <span class="val">{ESC(q["number"])}</span></p>
  <p>{ESC(q["note"])}</p>
  {table}
  <p class="small muted">Instability indices here are computed over cation
  sites only. They depend on the structure family: the often-quoted
  0.20 v.u. comes from simple ordered structures, and spinels and many
  perovskites exceed it while being stable. Read the number against its
  family and beside the verdict. The three indices agree whenever every
  cation site carries the same occupancy; <span class="mono">gii_recommended</span>
  names the one that fits this structure.</p>
</section>'''


def _screens_section(result):
    e = _engine()
    aa_floor = getattr(e, 'ANION_ANION_MIN', 2.35)
    cc_floor = getattr(e, 'CATION_CATION_MIN', 2.40)

    def state(v):
        b = _bool(v)
        return {True: 'pass', False: 'fail', None: 'untested'}[b]

    nshift = int(_num(_sv(result, 'n_sites_shift_proposed')) or 0)
    ncn = _num(_sv(result, 'n_sites_cn_implausible'))
    rows = [
        ('Radii ratio', 'Shortest cation–anion contact against the '
         'Shannon radii', state(_sv(result, 'structure_core_geometry_plausible')),
         f'shortest contact at {_f(_sv(result, "structure_core_shortest_contact_ratio"))} '
         f'of the radii sum'),
        ('Bond-valence distance', 'The same contact against the ion’s own '
         'bond valence parameters', state(_sv(result, 'structure_bvs_geometry_plausible')),
         f'shortest contact at {_f(_sv(result, "structure_bvs_distance_ratio"))} '
         f'of the implied distance'),
        ('Anion packing', 'Two anions closer than their electron clouds allow',
         state(_sv(result, 'anion_packing_plausible')),
         f'shortest anion–anion {_f(_sv(result, "anion_anion_min"))} Å; '
         f'floor {aa_floor:g} Å'),
        ('Cation packing', 'The same for the cation sublattice',
         state(_sv(result, 'cation_packing_plausible')),
         f'shortest cation–cation {_f(_sv(result, "cation_cation_min"))} Å; '
         f'floor {cc_floor:g} Å'),
        ('Coordination', 'Whether bonds are missing, rather than too short',
         state(_sv(result, 'structure_cn_plausible')),
         ('every coordination number within the tabulated range'
          if not ncn else f'{int(ncn)} site(s) outside the tabulated range')),
        ('Half-lattice shift', 'Whether a cation sits on the wrong origin',
         'fail' if nshift else 'pass',
         (pretty(_sv(result, 'shift_evidence')) or f'{nshift} site(s) proposed')
         if nshift else 'no cation proposed for a shift'),
    ]
    body = ''.join(
        f'<tr class="{st}"><td><span class="dot" aria-hidden="true"></span>'
        f'<b>{ESC(n)}</b><br><span class="muted small">{ESC(what)}</span></td>'
        f'<td class="st">{ {"pass": "passed", "fail": "failed", "untested": "not tested"}[st] }</td>'
        f'<td>{ESC(m)}</td></tr>'
        for n, what, st, m in rows)
    return f'''
<section>
  <h3>Geometry screens</h3>
  <p class="small muted">Six independent screens, reported separately
  because they see different things. They feed the G and M facets; a failed
  screen is not by itself a verdict.</p>
  <table class="screens"><tbody>{body}</tbody></table>
</section>'''


def _sites_section(result, x):
    s = result.sites
    if s is None or not len(s):
        return ''
    expunged = x['tier'] == 'EXPUNGE'
    rows = []
    for _, r in s.iterrows():
        z = _num(r.get('bond_size_z'))
        code = _str(r.get('pgrm_code')) or '-'
        zt = '' if z is None else f'{z + 0.0:+.1f}'.replace('-0.0', '0.0').replace('+0.0', '0.0')
        exp = _num(r.get('bl_expected_mean'))
        sd = _num(r.get('bl_expected_sd'))
        bvs = _num(r.get('bvs'))
        bsig = _num(r.get('bvs_sigma'))
        dev = _num(r.get('bvs_percent_diff'))
        dom = _bool(r.get('is_dominant_species'))
        rows.append(
            f'<tr class="{"minor" if dom is False else ""}">'
            f'<td>{ESC(_str(r.get("site_label")) or "")}</td>'
            f'<td>{ion_html(r.get("element"), r.get("valence"))}</td>'
            f'<td class="n">{_f(r.get("occupancy"), 3)}</td>'
            f'<td class="n">{ESC(str(r.get("cn")))}</td>'
            f'<td class="n">{_f(r.get("econ"), 2)}</td>'
            f'<td>{ESC(_str(r.get("geometry")) or "")}</td>'
            f'<td class="n">{_f(r.get("avg_bond_length"))}</td>'
            f'<td class="n">{"" if exp is None else f"{exp:.3f}"}'
            f'{"" if sd is None else f" ± {sd:.3f}"}</td>'
            f'<td class="n">{zt}</td>'
            f'<td class="n{" struck" if expunged else ""}">{_f(bvs)}'
            f'{"" if bsig is None else f" ± {bsig:.3f}"}</td>'
            f'<td class="n{" struck" if expunged else ""}">'
            f'{"" if dev is None else f"{dev:+.1f}%"}</td>'
            f'<td class="mono">{ESC(code)}</td></tr>')
    note = ('<p class="small muted">Bond valence sums are shown struck '
            'through: they are arithmetic on coordinates Eir judges '
            'impossible, kept for diagnosis only.</p>' if expunged else '')
    return f'''
<section>
  <h3>Sites</h3>
  <div class="scroll"><table class="sites">
  <thead><tr><th>Site</th><th>Ion</th><th>Occ.</th><th>CN</th><th>ECoN</th>
  <th>Geometry</th><th>Mean bond (Å)</th><th>Measured mean (Å)</th>
  <th>z</th><th>BVS (v.u.)</th><th>vs valence</th><th>Code</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table></div>
  <p class="small muted">One row per species on each cation position; rows
  in grey are minority species on a shared position. <i>Measured mean</i> is
  the mean, &plusmn; one standard deviation, over every bond of that ion in that
  coordination in Gagn&eacute;&rsquo;s surveys; <i>z</i> is the site&rsquo;s
  mean bond against it in those standard deviations
  (<span class="mono">bond_size_z</span>). <i>vs valence</i> is the bond
  valence sum against the assigned valence
  (<span class="mono">bvs_percent_diff</span>).</p>
  {note}
</section>'''


def _polyhedra_section(result, x, limit=12):
    pos = _positions(result.sites)
    if not pos:
        return ''
    head = x['site']
    head_lab = _str(head.get('site_label')) if head is not None else None
    # the headline site first, then any failing ones, then the rest
    def rank(t):
        row = t[0]
        lab = _str(row.get('site_label'))
        code = _str(row.get('pgrm_code')) or '-'
        return (0 if lab == head_lab else 1 if code[0] in 'GPR' else 2)
    pos = sorted(pos, key=rank)
    figs, skipped = [], 0
    for row, grp in pos:
        if len(figs) >= limit:
            skipped += 1
            continue
        hl = None
        lab = _str(row.get('site_label'))
        if lab == head_lab and result.code in ('G1', 'G6', 'M8'):
            hl = 'shortest_bond'
        elif result.code == 'G2':
            hl = 'anion_pair'
        png, pairs = _draw_polyhedron(result.cif, row, hl)
        shared = ''
        if len(grp) > 1 and 'occupancy' in grp.columns:
            shared = ' / '.join(
                f'{ESC(str(g.get("element")))} {_f(g.get("occupancy"), 3)}'
                for _, g in grp.iterrows())
        cap = [f'<b>{ESC(lab or "")}</b> {ion_html(row.get("element"), row.get("valence"))}, '
               f'CN {ESC(str(row.get("cn")))}'
               + (f', {ESC(_str(row.get("geometry")))}' if _str(row.get("geometry")) else '')]
        if pairs:
            cap.append(_bond_summary(str(row.get('element')), pairs))
        if shared:
            cap.append(f'shared: {shared}')
        if hl == 'shortest_bond':
            cap.append('<span class="hot">shortest bond in red</span>')
        if hl == 'anion_pair' and png:
            cap.append('<span class="hot">closest anion pair in red, where it '
                       'lies in this polyhedron</span>')
        img = (f'<img alt="Coordination polyhedron of {ESC(lab or "")}" '
               f'src="data:image/png;base64,{base64.b64encode(png).decode()}">'
               if png else '<div class="noimg">not drawn</div>')
        figs.append(f'<figure>{img}<figcaption>{"<br>".join(cap)}</figcaption></figure>')
    more = (f'<p class="small muted">{skipped} more position(s) not drawn.</p>'
            if skipped else '')
    return f'''
<section>
  <h3>Coordination polyhedra</h3>
  <p class="small muted">Each cation position and its first shell, from the
  same symmetry expansion the bond valence sums use. Drawn to scale, in
  orthographic projection.</p>
  <div class="polys">{''.join(figs)}</div>{more}
</section>'''


def _anion_section(result):
    n = _num(_sv(result, 'n_anion_sites'))
    if not n:
        return ''
    bal = _bool(_sv(result, 'anion_balances'))
    worst = _str(_sv(result, 'anion_worst_label'))
    return f'''
<section>
  <h3>Anions</h3>
  <p>{int(n)} anion position(s); mean anion bond valence sum
  {_f(_sv(result, "anion_bvs_mean"))} v.u.; largest deviation
  {_f(_sv(result, "anion_deviation_max"))} v.u.
  {f"at {ESC(worst)}" if worst else ""}{_ligand_text(_sv(result, 'anion_worst_ligands'))}.
  {'The anion sums balance.' if bal else 'The anion sums do not balance.' if bal is False else ''}</p>
</section>'''


def _ligand_text(s):
    s = _str(s)
    if not s:
        return ''
    parts = []
    for tok in s.split(','):
        if ':' in tok:
            el, n = tok.split(':', 1)
            parts.append(f'{ESC(n.strip())} {ESC(el.strip())}')
        else:
            parts.append(ESC(tok.strip()))
    return ' (bonded to ' + ', '.join(parts) + ')'


def _provenance_section(result):
    e = _engine()
    run = result.run
    ox = (run.oxidation_states if run is not None else None) or {}
    src = ''
    if result.sites is not None and 'valence_source' in result.sites.columns:
        vs = sorted({str(v) for v in result.sites['valence_source'].dropna()})
        src = ', '.join(vs)
    try:
        sha = hashlib.sha256(result.cif.read_bytes()).hexdigest()[:16]
    except OSError:
        sha = 'unavailable'
    st = result.structure
    meta = []
    for k, label in (('icsd_code', 'ICSD collection code'), ('year', 'Published'),
                     ('journal', 'Journal'), ('authors', 'Authors'),
                     ('measurement_conditions', 'Conditions')):
        v = _str(st.get(k)) if st is not None else None
        if v and v not in ('nan', 'unknown'):
            if k == 'year':
                v = v.split('.')[0]
            meta.append(f'<dt>{label}</dt><dd>{ESC(v)}</dd>')
    cfg = []
    if result.sites is not None:
        for c in result.sites.columns:
            if c.startswith('cfg_'):
                v = result.sites[c].dropna()
                if len(v):
                    cfg.append(f'{c[4:]} = {v.iloc[0]}')
    oxs = ', '.join(f'{ESC(k)} {float(v):+g}' for k, v in sorted(ox.items()))
    return f'''
<section class="prov">
  <h3>How this was produced</h3>
  <dl class="kv">
    {''.join(meta)}
    <dt>File</dt><dd class="mono">{ESC(result.cif.name)} (SHA-256 {sha}&hellip;)</dd>
    <dt>Eir</dt><dd>engine {ESC(getattr(e, "EIR_VERSION", "?"))}, package
      eir-bvs {ESC(__version__)}</dd>
    <dt>Run</dt><dd>{_dt.datetime.now().strftime("%Y-%m-%d %H:%M")}</dd>
    <dt>Oxidation states</dt><dd>{oxs or "from the file"}{f" <span class='muted'>(source: {ESC(src)})</span>" if src else ""}</dd>
    <dt>Bond valence parameters</dt><dd>Gagn&eacute; and Hawthorne (2015), with
      Brown (2020) where they give none; not Brown and Altermatt (1985)</dd>
    <dt>Bond lengths</dt><dd>Gagn&eacute;&rsquo;s aggregated surveys of measured
      structures</dd>
    <dt>Settings</dt><dd class="mono small">{ESC("; ".join(cfg))}</dd>
    {''.join(f'<dt>Note</dt><dd class="small">{ESC(n)}</dd>' for n in (run.notes if run is not None else []))}
  </dl>
</section>'''


CSS = r'''
:root{--bg:#ffffff;--fg:#131E29;--muted:#5b6470;--line:#d9dce1;--card:#f6f7f9;
--ok:#005750;--ok-bg:#e3f4f0;--warn:#a34700;--warn-bg:#fff1e6;--na:#4b3f8f;
--na-bg:#efecfb;--bad:#c4003f;--bad-bg:#fde8ee;--accent:#440099}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11161c;
--fg:#e8eaed;--muted:#9aa3ad;--line:#2c333b;--card:#181e25;--ok:#3bd4ae;
--ok-bg:#0f2a25;--warn:#ff9664;--warn-bg:#2d1d12;--na:#a78cfa;--na-bg:#211b38;
--bad:#ff6371;--bad-bg:#30141b;--accent:#a78cfa}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 -apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.page{max-width:920px;margin:0 auto;padding:28px 20px 48px}
header .brand{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header h1{font-size:26px;margin:4px 0 2px;font-weight:650}
header .sub{color:var(--muted);margin:0}
h2{font-size:22px;margin:0}
h3{font-size:16px;margin:0 0 8px;font-weight:650}
section{margin-top:22px}
.verdict{border-radius:12px;padding:18px 20px;border:1px solid var(--line);background:var(--card)}
.verdict.ok{background:var(--ok-bg);border-color:transparent}
.verdict.warn{background:var(--warn-bg);border-color:transparent}
.verdict.na{background:var(--na-bg);border-color:transparent}
.verdict.bad{background:var(--bad-bg);border-color:transparent}
.tierline{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px}
.tier{font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
letter-spacing:.04em;padding:6px 9px;border-radius:6px;color:#fff}
.ok .tier{background:var(--ok)}.warn .tier{background:var(--warn)}
.na .tier{background:var(--na)}.bad .tier{background:var(--bad)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tier{color:#11161c}}
.meaning{margin:10px 0 0}
.reason{margin:10px 0 0;font-weight:600}
.caution{margin:12px 0 0;padding:10px 12px;border-left:3px solid var(--warn);
background:var(--bg);border-radius:4px;font-size:14px}
.kv{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;margin:10px 0 0}
.kv dt{color:var(--muted)}.kv dd{margin:0;min-width:0;overflow-wrap:anywhere}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em}
.muted{color:var(--muted)}.small{font-size:13px}
.facets{list-style:none;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;
padding:0;margin:16px 0 0}
.facet{background:var(--bg);border-radius:8px;padding:8px 10px;display:flex;
flex-direction:column;border:1px solid var(--line)}
.facet .fl{font-weight:700}.facet .fn{font-size:13px}.facet .fs{font-size:12px;color:var(--muted)}
.facet.pass .fl{color:var(--ok)}.facet.fail .fl{color:var(--bad)}
.facet.caveat .fl{color:var(--na)}.facet.not-reached{opacity:.55}
.quote{border:1px solid var(--line);border-radius:12px;padding:16px 20px}
.quote .big{margin:0 0 6px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.quote .idx{color:var(--muted)}
.quote .val{font-size:28px;font-weight:650;font-variant-numeric:tabular-nums}
.quote.withheld .val{text-decoration:line-through;color:var(--muted)}
.quote.partial .val,.quote.caveat .val{color:var(--muted)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600}
td.n,th.n{text-align:right;white-space:nowrap}
.indices tr.rec td{font-weight:650}
.screens td.st{white-space:nowrap;font-weight:600}
.screens tr.pass td.st{color:var(--ok)}.screens tr.fail td.st{color:var(--bad)}
.screens tr.untested td.st{color:var(--muted)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;background:var(--line)}
.screens tr.pass .dot{background:var(--ok)}.screens tr.fail .dot{background:var(--bad)}
.scroll{overflow-x:auto}
.sites{font-size:13.5px}.sites tr.minor td{color:var(--muted)}
.struck{text-decoration:line-through;color:var(--muted)}
.polys{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
figure{margin:0;border:1px solid var(--line);border-radius:10px;padding:8px;background:var(--card)}
figure img{width:100%;height:auto;display:block}
figcaption{font-size:12.5px;line-height:1.4;margin-top:4px}
.noimg{height:120px;display:grid;place-items:center;color:var(--muted)}
.hot{color:var(--bad)}
.bar{text-decoration:overline}
footer{margin-top:30px;padding-top:14px;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}
@media (max-width:600px){.facets{grid-template-columns:repeat(2,1fr)}.quote .val{font-size:24px}}
@media print{body{font-size:12px}.page{padding:0}section{break-inside:avoid}
.verdict,.quote,figure{border:1px solid #ccc}}
'''


def build_report(result, fragment=False):
    """The report as HTML: a whole page, or a fragment for a notebook."""
    x = explain(result)
    st = result.structure
    formula = formula_html(st.get('chemical_formula')) if st is not None else ''
    sg = spacegroup_html(st.get('space_group')) if st is not None else ''
    sub = ' &middot; '.join(p for p in (formula, sg) if p)
    body = f'''
<div class="page">
<header>
  <div class="brand">Eir &middot; structure report</div>
  <h1>{ESC(result.cif.name)}</h1>
  <p class="sub">{sub}</p>
</header>
{_verdict_section(result, x)}
{_quote_section(result, x)}
{'' if result.failure else _screens_section(result)}
{'' if result.failure else _sites_section(result, x)}
{'' if result.failure else _polyhedra_section(result, x)}
{'' if result.failure else _anion_section(result)}
{_provenance_section(result)}
<footer>
  If you use this result, please cite N. Reeves-McLaren, <i>Dalton Trans.</i>,
  2026, <b>55</b>, 2868 (doi:10.1039/D5DT03003J), name the Eir version above,
  and cite the reference data: Gagn&eacute; and Hawthorne, <i>Acta Cryst.</i>
  2015, <b>B71</b>, 562, and Gagn&eacute;&rsquo;s bond length surveys.
  Eir is open source: github.com/SuperBladesman/Eir.
</footer>
</div>'''
    if fragment:
        return (f'<div class="eir-report"><style>{_scoped(CSS)}</style>'
                f'{body}</div>')
    title = f'Eir report: {result.cif.stem}'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{ESC(title)}</title><style>{CSS}</style></head>'
            f'<body>{body}</body></html>')


def _scoped(css):
    """Scope the page CSS to .eir-report, for display inside a notebook."""
    css = css.replace(':root:not([data-theme="light"])', '.eir-report')
    css = css.replace(':root', '.eir-report')
    css = re.sub(r'(^|})\s*body\{', r'\1.eir-report{', css)
    css = re.sub(r'(^|})\s*\*\{', r'\1.eir-report *{', css)
    return css
