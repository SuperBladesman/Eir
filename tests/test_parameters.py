"""The bond valence parameter table, and what Eir does where it has no entry.

The table is keyed (cation, valence, anion) without the anion's charge, so
each entry records the charge it was fitted for. Until 2.0.46 the table held
rows fitted for other anion charges (Brown's Pr3+-Se(1-) used for Pr3+-Se(2-))
and 32 values labelled Brown (2020) that are in none of the 2009, 2011 and
2020 releases of Brown's compilation. Chen and Adams (2017) then fill gaps and
replace unpublished values. The structures here are small and synthetic.
"""
import ast
import json
from pathlib import Path

import pytest

import eir

DATA = Path(__file__).resolve().parents[1] / 'Data'
# the charge Eir gives each anion (ALWAYS_ANION and AMPHOTERIC_ANION)
ANION = {'O': -2, 'F': -1, 'Cl': -1, 'Br': -1, 'I': -1, 'S': -2, 'Se': -2,
         'Te': -2, 'N': -3, 'P': -3, 'As': -3, 'H': -1, 'C': -4, 'Si': -4,
         'B': -3}


@pytest.fixture(scope='module')
def table():
    return json.loads((DATA / 'bvs_parameters.json').read_text())


def test_every_entry_is_for_the_charge_eir_gives_its_anion(table):
    wrong = [k for k, v in table.items()
             if v.get('anion_charge') != ANION.get(ast.literal_eval(k)[2])]
    assert not wrong, wrong[:10]


def test_every_entry_names_its_source(table):
    refs = {v['reference'] for v in table.values()}
    assert refs == {'Gagne2015', 'Brown_2020', 'Brown_2009_Table2_ref54',
                    'ChenAdams2017_softNC1'}, refs
    assert all(v.get('brown_code') for v in table.values()
               if v['reference'] in ('Gagne2015', 'Brown_2020'))
    # Chen and Adams (2017) fits are used only where at least three
    # environments were fitted
    assert all(v.get('n_environments', 0) >= 3 for v in table.values()
               if v['reference'] == 'ChenAdams2017_softNC1')


def test_published_fits_outrank_unpublished_values(table):
    # Ni3+-O: Brown lists only his private communication (1.75, b 0.37);
    # Chen and Adams (2017) fit 15 environments
    ni = table["('Ni', 3, 'O')"]
    assert ni['reference'] == 'ChenAdams2017_softNC1'
    assert (ni['r0'], ni['b']) == (1.6565, 0.414)


def test_the_excluded_entries_are_not_in_the_table(table):
    gone = json.loads((DATA / 'bvs_parameters_excluded.json').read_text())
    gone.pop('_about')
    assert gone and all(v.get('reason') for v in gone.values())
    for k, v in gone.items():
        if k in table:
            # replaced, or removed and later filled: the table holds a
            # different value from another source, and the reason says so
            assert ('replaced' in v['reason'] or 'now takes' in v['reason']), k
            assert (table[k]['r0'], table[k]['b']) != (v['r0'], v['b']), k


def cif(name, a, cat, cq, an, aq, anion_at):
    return '\n'.join([
        f'data_{name}', f'_cell_length_a {a}', f'_cell_length_b {a}',
        f'_cell_length_c {a}', '_cell_angle_alpha 90', '_cell_angle_beta 90',
        '_cell_angle_gamma 90', "_symmetry_space_group_name_H-M 'F m -3 m'",
        'loop_', '_atom_type_symbol', '_atom_type_oxidation_number',
        f'{cat}{cq}+ {cq}', f'{an}{-aq}- {aq}',
        'loop_', '_atom_site_label', '_atom_site_type_symbol',
        '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z',
        '_atom_site_occupancy',
        f'{cat}1 {cat}{cq}+ 0 0 0 1', f'{an}1 {an}{-aq}- {anion_at} 1']) + '\n'


@pytest.mark.parametrize('name, text', [
    # no Ra-O parameters at any valence
    ('rao', cif('rao', 5.58, 'Ra', 2, 'O', -2, '0.5 0.5 0.5')),
    # no Pm3+-O parameters in any source Eir uses
    ('pmo', cif('pmo', 5.10, 'Pm', 3, 'O', -2, '0.5 0.5 0.5')),
    # no Pr4+-O row in any source Eir uses
    ('pro2', cif('pro2', 5.39, 'Pr', 4, 'O', -2, '0.25 0.25 0.25')),
])
def test_no_parameters_is_not_assessed_not_expunged(tmp_path, name, text):
    p = tmp_path / f'{name}.cif'
    p.write_text(text)
    r = eir.check(p)
    assert r.tier == 'NOT_ASSESSED', (r.tier, r.reason)
    assert r.reason == 'no_bond_valence_parameters', r.reason
