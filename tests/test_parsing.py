"""Files written the way other programs and older files write them.

Each case is a small synthetic structure (nothing here comes from the ICSD),
run end to end through eir.check, as a user would run it. Every case is one
that engine 2.0.45 got wrong: a charge lost, a crash, a file that vanished,
a hydride dropped from a sum, a hydroxide expunged for its O-H bond. Add a
case whenever a new way of writing a file turns up; VALIDATE_PARSING() in
the notebook holds the same cases at the level of the engine.
"""
import pytest

import eir

RUT = (4.7374, 4.7374, 3.1864, 90, 90, 90)
BRU = (3.142, 3.142, 4.766, 90, 90, 120)


def cif(name, cell, sg, sites, loop=None, type_col=True, formula=None):
    a, b, c, al, be, ga = cell
    s = [f'data_{name}', f'_cell_length_a {a}', f'_cell_length_b {b}',
         f'_cell_length_c {c}', f'_cell_angle_alpha {al}', f'_cell_angle_beta {be}',
         f'_cell_angle_gamma {ga}', f"_symmetry_space_group_name_H-M '{sg}'"]
    if formula:
        s.append(f"_chemical_formula_sum '{formula}'")
    if loop:
        s += ['loop_', '_atom_type_symbol', '_atom_type_oxidation_number']
        s += [f'{t} {v}' for t, v in loop]
    s += ['loop_', '_atom_site_label'] + (['_atom_site_type_symbol'] if type_col else [])
    s += ['_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z',
          '_atom_site_occupancy']
    for lab, typ, x, y, z, occ in sites:
        s.append(' '.join([lab] + ([typ] if type_col else [])
                          + [str(x), str(y), str(z), str(occ)]))
    return '\n'.join(s) + '\n'


def cubic(a):
    return (a, a, a, 90, 90, 90)


def sno2(t_sn, t_o, l_sn='Sn1', type_col=True, loop=None):
    return cif('sno2', RUT, 'P 42/m n m',
               [(l_sn, t_sn, 0, 0, 0, 1), ('O1', t_o, 0.3056, 0.3056, 0, 1)],
               loop, type_col)


def run(tmp_path, text, ox=None):
    p = tmp_path / 'x.cif'
    p.write_text(text)
    return eir.check(p, oxidation_states=ox)


def site(r, element):
    s = r.sites[r.sites['element'] == element]
    assert len(s) == 1, f'{element} sites: {list(r.sites["element"])}'
    return s.iloc[0]


OXSN = {'Sn': 4, 'O': -2}


@pytest.mark.parametrize('text, ox', [
    (sno2('Sn4+', 'O2-', loop=[('Sn4+', 4), ('O2-', -2)]), None),   # ICSD
    (sno2('Sn+4', 'O-2'), None),                                    # GSAS-II
    (sno2('SN4+', 'O2-'), None),                                    # upper case
    (sno2(None, None, type_col=False), OXSN),                       # no type column
    (sno2(None, None, 'SN1', type_col=False), OXSN),                # ... upper-case label
    (sno2('Sn', 'O'), OXSN),                                        # no charges
], ids=['icsd', 'gsas', 'upper', 'no-type', 'no-type-upper', 'no-charge'])
def test_tin_is_tin_at_four(tmp_path, text, ox):
    r = run(tmp_path, text, ox)
    assert r.readable
    s = site(r, 'Sn')
    assert float(s['valence']) == 4.0
    assert (r.tier, r.code) == ('ACCEPT', '-')


def test_upper_case_cobalt_does_not_stop_the_run(tmp_path):
    # 'CO2+' with no oxidation-number loop: 2.0.45 read 'O2+' out of it.
    r = run(tmp_path, cif('coo', cubic(4.26), 'F m -3 m',
                          [('Co1', 'CO2+', 0, 0, 0, 1), ('O1', 'O2-', 0.5, 0.5, 0.5, 1)]))
    assert float(site(r, 'Co')['valence']) == 2.0
    assert r.tier == 'ACCEPT'


def test_decimal_in_the_symbol(tmp_path):
    r = run(tmp_path, cif('mno', cubic(4.445), 'F m -3 m',
                          [('Mn1', 'Mn2.5+', 0, 0, 0, 1), ('O1', 'O2-', 0.5, 0.5, 0.5, 1)]))
    assert float(site(r, 'Mn')['valence']) == pytest.approx(2.5)


def smho(ts, to, th, loop=None):
    return cif('smho', cubic(5.4695), 'F m -3 m',
               [('Sm1', ts, 0, 0, 0, 1), ('O1', to, 0.25, 0.25, 0.25, 0.5),
                ('H1', th, 0.25, 0.25, 0.25, 0.5)], loop)


@pytest.mark.parametrize('text, ox', [
    (smho('Sm3+', 'O2-', 'H1-', [('Sm3+', 3), ('O2-', -2), ('H1-', -1)]), None),
    (smho('Sm', 'O', 'H'), {'Sm': 3, 'O': -2, 'H': -1}),
], ids=['in-the-cif', 'supplied'])
def test_hydride_sharing_oxygens_position_is_summed(tmp_path, text, ox):
    r = run(tmp_path, text, ox)
    assert float(site(r, 'Sm')['bvs']) == pytest.approx(3.14, abs=0.02)
    assert r.tier == 'ACCEPT'


@pytest.mark.parametrize('h', ['H1+', 'D1+'])
def test_hydroxide_with_hydrogen_located(tmp_path, h):
    # Mg(OH)2: 2.0.45 expunged it on G1 for the 0.98 A O-H bond, and did
    # not recognise D at all.
    r = run(tmp_path, cif('bru', BRU, 'P -3 m 1',
                          [('Mg1', 'Mg2+', 0, 0, 0, 1),
                           ('O1', 'O2-', 0.33333, 0.66667, 0.2221, 1),
                           ('H1', h, 0.33333, 0.66667, 0.4275, 1)],
                          [('Mg2+', 2), ('O2-', -2), (h, 1)]))
    assert (r.tier, r.code) == ('ACCEPT', '-')
    assert float(site(r, 'H')['bvs']) == pytest.approx(1.0, abs=0.1)


def test_labels_read_against_the_formula(tmp_path):
    # Upper-case labels and no type column: HO1 is hydrogen in Mg(OH)2.
    r = run(tmp_path, cif('bru', BRU, 'P -3 m 1',
                          [('MG1', None, 0, 0, 0, 1),
                           ('O1', None, 0.33333, 0.66667, 0.2221, 1),
                           ('HO1', None, 0.33333, 0.66667, 0.4275, 1)],
                          type_col=False, formula='H2 Mg1 O2'),
            {'Mg': 2, 'O': -2, 'H': 1})
    assert set(r.sites['element']) == {'Mg', 'H'}


@pytest.mark.parametrize('anion, text', [
    ('O/F', cif('nbo2f', cubic(3.902), 'P m -3 m',
                [('Nb1', 'Nb5+', 0, 0, 0, 1), ('O1', 'O2-', 0.5, 0, 0, 0.6667),
                 ('F1', 'F1-', 0.5, 0, 0, 0.3333)],
                [('Nb5+', 5), ('O2-', -2), ('F1-', -1)])),
    ('S/Se', cif('pbsse', cubic(6.03), 'F m -3 m',
                 [('Pb1', 'Pb2+', 0, 0, 0, 1), ('S1', 'S2-', 0.5, 0.5, 0.5, 0.5),
                  ('Se1', 'Se2-', 0.5, 0.5, 0.5, 0.5)],
                 [('Pb2+', 2), ('S2-', -2), ('Se2-', -2)])),
], ids=['oxyfluoride', 'sulfoselenide'])
def test_shared_anion_positions(tmp_path, anion, text):
    r = run(tmp_path, text)
    second = anion.split('/')[1]
    cation = r.sites.iloc[0]
    assert len(r.sites) == 1, list(r.sites['element'])   # no anion read as a cation
    assert second in str(cation['colocated_ligands'])


@pytest.mark.parametrize('text', [
    cif('mg2sn', cubic(6.765), 'F m -3 m',
        [('Sn1', 'Sn4-', 0, 0, 0, 1), ('Mg1', 'Mg2+', 0.25, 0.25, 0.25, 1)],
        [('Sn4-', -4), ('Mg2+', 2)]),
    cif('insb', cubic(6.479), 'F -4 3 m',
        [('In1', 'In3+', 0, 0, 0, 1), ('Sb1', 'Sb3-', 0.25, 0.25, 0.25, 1)],
        [('In3+', 3), ('Sb3-', -3)]),
], ids=['Mg2Sn', 'InSb'])
def test_zintl_anions_are_not_assessed_and_say_why(tmp_path, text):
    r = run(tmp_path, text)
    assert (r.tier, r.code, r.reason) == ('NOT_ASSESSED', 'R1', 'unsupported_anion')
    assert 'typed as an anion' in r.evidence
    assert 'Zintl' in r.verdict()
    assert '<html' in r.report_html().lower()
