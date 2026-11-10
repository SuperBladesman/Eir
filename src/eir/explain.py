"""Plain-English readings of Eir's verdicts.

The engine reports a tier (structure_pgrm_tier), a code (G2, M8, ...), a
reason (anion_packing_impossible, ...) and the measurement that decided it.
This module turns those into sentences. It decides nothing: every sentence is
a reading of a column the engine wrote, and the code and the measurement are
always shown beside it.
"""

import re

# tier -> (short headline, what it means for the reader)
TIERS = {
    'ACCEPT': (
        'Nothing wrong found',
        'Eir found nothing wrong with this structure. Its bond valence '
        'result can be quoted.'),
    'ACCEPT_IMPRECISE': (
        'Sound, but imprecise',
        'Eir found nothing wrong with this structure, but the coordinate '
        'uncertainties in the file are too large to fix the instability '
        'index closely. Quote the index with its uncertainty.'),
    'ACCEPT_HOMOVALENT': (
        'Sound, with a shared site',
        'Eir found nothing wrong with this structure. More than one species '
        'shares a crystallographic position, all with the same valence; that '
        'is normal for many structure types, and the index Eir recommends '
        'allows for it.'),
    'ACCEPT_HETEROVALENT': (
        'Sound, with a mixed-valence shared site',
        'Eir found nothing wrong with this structure. Ions whose valences '
        'differ by two or more share a crystallographic position, which a '
        'bond valence sum cannot separate. The index Eir recommends allows '
        'for the sharing; whether to accept the model is a judgement for '
        'the reader.'),
    'FLAG': (
        'Ambiguous',
        'The analysis stands, but something about the model in the file '
        'leaves the result open to question. The reason is below.'),
    'NOT_ASSESSED': (
        'Not fully assessed',
        'Eir lacks reference data for at least one ion, so part of the '
        'assessment could not be made. This says nothing about whether the '
        'structure is right.'),
    'EXPUNGE': (
        'Cannot be right',
        'The atoms cannot be where the file puts them. No bond valence '
        'result from this file should be quoted.'),
}

FACETS = [('P', 'Parse', 'Can the file be read?'),
          ('G', 'Geometry', 'Can the atoms be where the file puts them?'),
          ('R', 'Reference', 'Is there reference data to assess it?'),
          ('M', 'Model', 'Is the model in the file unambiguous?')]

INDEX_NAMES = {
    'gii': ('GII', 'global instability index, every cation site weighted '
                   'equally'),
    'wagii': ('WAGII', 'instability index weighted by site occupancy'),
    'gii_site_averaged': ('site-averaged GII', 'instability index with the '
                          'sums on each shared position combined first'),
}


def pretty(s):
    """Typeset an evidence string: angstroms, plus-minus, arrows."""
    if s is None:
        return ''
    s = str(s)
    s = re.sub(r'(\d) A\b', '\\1 Å', s)
    s = s.replace('+/-', '±').replace(' -> ', ' → ')
    s = re.sub(r'anion-anion', 'anion–anion', s)
    s = re.sub(r'cation-cation', 'cation–cation', s)
    return s


def _ion(site):
    if site is None:
        return 'one ion'
    el, v = site.get('element'), site.get('valence')
    try:
        v = float(v)
        sign = '+' if v > 0 else '−'
        vv = f'{abs(v):g}'
        return f'{el}{vv}{sign}' if vv != '1' else f'{el}{sign}'
    except (TypeError, ValueError):
        return str(el)


def _at(site):
    if site is None:
        return ''
    lab = site.get('site_label')
    return f' (site {lab})' if lab not in (None, '') else ''


def _ligands(site):
    if site is None:
        return None
    lt = site.get('ligand_types')
    if lt is None or lt != lt:
        return None
    found = re.findall(r'[A-Z][a-z]?', str(lt))
    return ', '.join(dict.fromkeys(found)) or None


def _a_site(site):
    lab = None if site is None else site.get('site_label')
    return f'Site {lab}' if lab not in (None, '') else 'A site'


# Where a code makes the tier's general meaning inexact.
CODE_MEANING = {
    'P': 'The file cannot be read, so nothing in it can be assessed.',
    'G7': ('The model in the file is missing bonds, so the sums built on it '
           'mean nothing. No bond valence result from this file should be '
           'quoted.'),
}


def _reason_sentence(code, reason, site):
    """One sentence, without numbers: the numbers are in the evidence."""
    ion, at = _ion(site), _at(site)
    lig = _ligands(site)
    el = site.get('element') if site is not None else None
    S = {
        'unreadable_file':
            'Eir could not read the file.',
        'unsupported_anion':
            'The file types an element as an anion that Eir has no bond '
            'valence parameters for in that role, as in a Zintl or '
            'intermetallic phase, so nothing in it can be assessed.',
        'no_position':
            f'{_a_site(site)} has no coordinates, so nothing can be computed '
            f'for it.',
        'contact_below_physical_floor':
            f'A contact to {ion}{at} is shorter than any chemical bond can '
            f'be.',
        'contact_below_measured_minimum':
            f'A bond to {ion}{at} is shorter, by more than a tenth, than any '
            f'yet measured for that ion in that coordination.',
        'no_coordination_shell':
            f'{ion}{at} has no neighbours within the search radius, so it '
            f'has no coordination shell to assess.',
        'cation_on_wrong_origin':
            f'{ion}{at} appears to sit half a lattice vector from its true '
            f'position. Eir tests this by moving it in a copy of the file '
            f'and re-running the whole analysis; the evidence says whether '
            f'the move resolved the fault.',
        'cation_position_suspect':
            f'The position of {ion}{at} looks wrong: moving it half a '
            f'lattice vector partly resolves its coordination shell.',
        'split_shell_cause_unknown':
            f'The first coordination shell of {ion}{at} is split in a way '
            f'that suggests a misplaced atom, but the cause could not be '
            f'established.',
        'split_shell_not_diagnostic':
            f'The first coordination shell of {ion}{at} is split, but '
            f'nothing else was failing, so testing a shifted position could '
            f'not decide anything.',
        'coordination_incomplete':
            f'{ion}{at} has fewer neighbours than the smallest coordination '
            f'tabulated for it, and its bond valence sum is less than half '
            f'its valence: bonds are missing from the model, so no sum '
            f'built on it can be trusted.',
        'anion_packing_impossible':
            'Two anions are closer together than their electron clouds '
            'allow.',
        'cation_packing_impossible':
            'Two cations are closer together than is credible for any sound '
            'structure.',
        'no_bond_valence_parameters':
            f'There are no bond valence parameters for {ion}'
            + (f' bonded to {lig}' if lig else '')
            + ', so its bond valence sum cannot be calculated.',
        'no_ionic_radius':
            f'There is no tabulated ionic radius for {ion}, so the radii '
            f'screen cannot be applied to it.',
        'no_measured_bond_lengths':
            f'Gagn\u00e9\u2019s bond length surveys have no measurements for '
            f'{ion}' + (f' bonded to {lig}' if lig else '')
            + ', so the checks against measured bond lengths cannot be made.',
        'no_index':
            'The recommended instability index could not be calculated.',
        'zero_occupancy':
            f'{_a_site(site)} is refined to zero occupancy: there is no atom '
            f'there.',
        'shortest_contact_implausible':
            f'The shortest contact to {ion}{at} is too short for the bond '
            f'length that ion\u2019s own bond valence parameters imply.',
        'polyhedron_size_implausible':
            f'The coordination polyhedron of {ion}{at} is the wrong size '
            f'for the ion in it, judged against every measured polyhedron '
            f'of that ion in that coordination.',
        'mixed_valence':
            f'{el or "An ion"}{at} is given a fractional valence. A bond '
            f'valence sum against an average valence cannot tell which ion '
            f'is which.',
        'pre_modern_determination':
            'The structure was determined before 1950, when diffraction '
            'intensities were mostly estimated by eye from film.',
        'shared_site_heterovalent':
            f'Ions whose valences differ by two or more share one '
            f'position{at}.',
        'shared_site_homovalent':
            f'More than one species shares a position{at}.',
        'partial_occupancy':
            f'{_a_site(site)} is only partly occupied.',
        'index_imprecise':
            'The coordinate uncertainties in the file leave the instability '
            'index imprecise.',
    }
    return S.get(reason) or (f'{code}: {reason}.' if reason else None)


def structure_value(result, col):
    """A structure-level value: the structure row, else the first site row
    that carries it (some structure-level columns live only in the site
    table)."""
    st = result.structure
    if st is not None and col in st.index:
        v = st.get(col)
        try:
            if v == v and str(v).strip() != '':
                return v
        except Exception:
            return v
    s = result.sites
    if s is not None and col in s.columns:
        vals = s[col].dropna()
        if len(vals):
            return vals.iloc[0]
    return None


SCREENS = [('radii ratio', 'structure_core_geometry_plausible'),
           ('bond-valence distance', 'structure_bvs_geometry_plausible'),
           ('anion packing', 'anion_packing_plausible'),
           ('cation packing', 'cation_packing_plausible'),
           ('coordination', 'structure_cn_plausible')]


def failed_screens(result):
    """Names of the geometry screens this structure failed."""
    if result.structure is None:
        return []
    out = [n for n, col in SCREENS
           if str(structure_value(result, col)).strip().lower() == 'false']
    try:
        if float(structure_value(result, 'n_sites_shift_proposed') or 0) > 0:
            out.append('half-lattice shift')
    except (TypeError, ValueError):
        pass
    return out


def headline_site(result):
    """The site row that carries the structure's code, if any."""
    s, code = result.sites, result.code
    if s is None or code in (None, '-', 'P') or 'pgrm_code' not in s.columns:
        return None
    hit = s[s['pgrm_code'] == code]
    if not len(hit):
        return None
    ev = result.evidence
    if ev is not None and 'pgrm_evidence' in hit.columns:
        same = hit[hit['pgrm_evidence'].astype(str) == str(ev)]
        if len(same):
            hit = same
    return hit.iloc[0]


def facet_states(code, tier):
    """{facet: 'pass' | 'fail' | 'caveat' | 'not reached'}"""
    if code is None:
        return {}
    gate = 'M' if code == '-' else code[0]
    out = {}
    order = [f for f, _, _ in FACETS]
    for f in order:
        if code == '-':
            out[f] = 'pass'
        elif order.index(f) < order.index(gate):
            out[f] = 'pass'
        elif f == gate:
            out[f] = ('caveat' if tier and tier.startswith('ACCEPT')
                      else 'fail')
        else:
            out[f] = 'not reached'
    return out


def _engine_or_none():
    try:
        from . import _engine as e
        return e
    except Exception:
        return None


def explain(result):
    """A dict of sentences describing the verdict on one structure."""
    e = _engine_or_none()
    tier = result.tier
    head, meaning = TIERS.get(tier, (tier or 'Unknown', ''))
    meaning = CODE_MEANING.get(result.code, meaning)
    site = headline_site(result)
    reason = (_reason_sentence(result.code, result.reason, site)
              if result.reason else None)
    q = result.quote
    quote = None
    if q is not None:
        name, val, sig = q
        short, long_ = INDEX_NAMES.get(name, (name, ''))
        num = f'{val:.3f}' + (f' ± {float(sig):.3f}' if sig is not None
                              and sig == sig else '') + ' v.u.'
        if tier in ('ACCEPT', 'ACCEPT_IMPRECISE', 'ACCEPT_HOMOVALENT',
                    'ACCEPT_HETEROVALENT'):
            quote = dict(status='quote', short=short, long=long_, number=num,
                         sentence=f'Quote {short} = {num}',
                         note='Eir recommends this index for this structure. '
                              'Quote it with its uncertainty.')
        elif tier == 'FLAG':
            quote = dict(status='caveat', short=short, long=long_, number=num,
                         sentence=f'{short} = {num}, quoted only with the '
                                  f'ambiguity above.',
                         note='Quote it only with the ambiguity above.')
        elif tier == 'NOT_ASSESSED':
            quote = dict(status='partial', short=short, long=long_, number=num,
                         sentence=f'Eir computed {short} = {num}, but could '
                                  f'not complete its checks, so it does not '
                                  f'vouch for the number.',
                         note='Eir could not complete its checks, so it does '
                              'not vouch for this number.')
        else:
            why = ('a shell that is missing bonds' if result.code == 'G7'
                   else 'coordinates that cannot be right')
            quote = dict(status='withheld', short=short, long=long_,
                         number=num,
                         sentence=f'Do not quote. Eir computed {short} = '
                                  f'{num}, but it is arithmetic on {why}.',
                         note=f'Do not quote it: it is arithmetic on {why}.')
    elif tier == 'EXPUNGE':
        quote = dict(status='withheld', short=None, long=None, number=None,
                     sentence='There is no bond valence result to quote.',
                     note='There is no bond valence result to quote.')
    return dict(tier=tier, headline=head, meaning=meaning, reason=reason,
                code=result.code, reason_key=result.reason,
                evidence=pretty(result.evidence), site=site, quote=quote,
                facets=facet_states(result.code, tier),
                failed_screens=failed_screens(result),
                screen_note=_screen_note(tier, result.code,
                                         failed_screens(result)))


# The screen each code reads, where one does.
_CODE_SCREEN = {'G2': 'anion packing', 'G5': 'cation packing',
                'G7': 'coordination',
                'M8': 'bond-valence distance', 'G4': 'half-lattice shift',
                'M7': 'half-lattice shift'}


def _screen_note(tier, code, failed):
    """Screens that failed without deciding the verdict."""
    rest = [f for f in failed if f != _CODE_SCREEN.get(code)]
    if not rest or tier in ('EXPUNGE', None):
        return None
    many = len(rest) > 1
    return (f'The {", ".join(rest)} screen{"s" if many else ""} failed. The '
            f'verdict does not rest on {"them" if many else "it"}, so check '
            f'{"them" if many else "it"} below before relying on the number.')


def verdict_text(result):
    """The verdict as a few lines for a terminal."""
    x = explain(result)
    s = result.structure
    name = result.cif.name
    bits = []
    if s is not None:
        f = s.get('chemical_formula')
        sg = s.get('space_group')
        if isinstance(f, str):
            bits.append(f)
        if isinstance(sg, str):
            bits.append(sg)
    lines = [f'{name}' + (f'  ·  {"  ·  ".join(bits)}' if bits else '')]
    lines.append('')
    lines.append(f'  {x["tier"]:<20} {x["headline"]}')
    if x['reason']:
        lines.append(_wrap(x['reason'], 23))
    if x['evidence']:
        lines.append(_wrap(x['evidence'], 23, first='  Evidence'))
    if x['code'] not in (None, '-', 'P'):
        lines.append(_wrap(f'{x["code"]} {x["reason_key"]}', 23,
                           first='  Code'))
    if x['quote']:
        lines.append(_wrap(x['quote']['sentence'], 23, first='  Bond valence'))
    if x['screen_note']:
        lines.append(_wrap(x['screen_note'], 23, first='  Screens'))
    return '\n'.join(lines)


def _wrap(text, indent, first=None, width=78):
    import textwrap
    pad = ' ' * indent
    init = (first.ljust(indent) if first else pad)
    return textwrap.fill(text, width=width, initial_indent=init,
                         subsequent_indent=pad)
