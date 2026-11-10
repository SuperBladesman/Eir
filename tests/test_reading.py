"""The reading stage, end to end: files written the way other programs write
them, through eir.check as a user would run it.

Each case is a FEATURE of a file, not the program that wrote it, and each is
a small synthetic structure; nothing here comes from the ICSD. Every case
but the last few was read wrongly, or not at all, by 2.0.46 before the
reading stage. VALIDATE_PARSING() in the notebook holds the same cases at
the level of the engine.
"""
import json

import pytest

import eir

RUT = (4.7374, 4.7374, 3.1864, 90, 90, 90)
BONDS = ('loop_\n_geom_bond_atom_site_label_1\n_geom_bond_atom_site_label_2\n'
         '_geom_bond_distance\n_geom_bond_site_symmetry_2\n')


def cif(name, cell, sg, sites, loop=None, extra=''):
    a, b, c, al, be, ga = cell
    s = [f'data_{name}', f'_cell_length_a {a}', f'_cell_length_b {b}',
         f'_cell_length_c {c}', f'_cell_angle_alpha {al}', f'_cell_angle_beta {be}',
         f'_cell_angle_gamma {ga}', f"_symmetry_space_group_name_H-M '{sg}'"]
    if extra:
        s.append(extra)
    if loop:
        s += ['loop_', '_atom_type_symbol', '_atom_type_oxidation_number']
        s += [f'{t} {v}' for t, v in loop]
    s += ['loop_', '_atom_site_label', '_atom_site_type_symbol', '_atom_site_fract_x',
          '_atom_site_fract_y', '_atom_site_fract_z', '_atom_site_occupancy']
    s += [' '.join(map(str, row)) for row in sites]
    return '\n'.join(s) + '\n'


def sno2(**k):
    labels = k.pop('labels', ('Sn1', 'O1'))
    return cif('sno2', RUT, 'P 42/m n m',
               [(labels[0], 'Sn4+', 0, 0, 0, 1), (labels[1], 'O2-', 0.3056, 0.3056, 0, 1)],
               [('Sn4+', 4), ('O2-', -2)], **k)


def run(tmp_path, text, ox=None, name='x.cif'):
    p = tmp_path / name
    p.write_text(text)
    return eir.check(p, oxidation_states=ox)


def tin(r):
    s = r.sites[r.sites['element'] == 'Sn']
    assert len(s) == 1, list(r.sites['element'])
    return float(s.iloc[0]['bvs'])


def notes(r):
    v = r.structure.get('cif_reading_notes')
    return '' if v is None or v != v else str(v)


@pytest.fixture(scope='module')
def tin_reference(tmp_path_factory):
    return tin(run(tmp_path_factory.mktemp('ref'), sno2()))


def test_a_file_in_order_is_read_as_it_is(tmp_path):
    r = run(tmp_path, sno2(extra='_database_code_ICSD 12345'))
    assert (r.tier, r.code) == ('ACCEPT', '-')
    assert notes(r) == ''
    assert r.structure['cif_database'] == 'ICSD 12345'
    assert r.structure['cif_read_from'] == 'x.cif'


def test_placeholder_bond_list_is_set_aside(tmp_path, tin_reference):
    r = run(tmp_path, sno2() + BONDS + '? ? ? ?\n')
    assert (r.tier, r.code) == ('ACCEPT', '-')
    assert tin(r) == pytest.approx(tin_reference, abs=1e-3)
    assert 'placeholders' in notes(r)


def test_partial_author_bond_list_is_set_aside(tmp_path):
    srt = cif('srtio3', (3.905,) * 3 + (90,) * 3, 'P m -3 m',
              [('Sr1', 'Sr2+', 0.5, 0.5, 0.5, 1), ('Ti1', 'Ti4+', 0, 0, 0, 1),
               ('O1', 'O2-', 0.5, 0, 0, 1)],
              [('Sr2+', 2), ('Ti4+', 4), ('O2-', -2)])
    r = run(tmp_path, srt + BONDS + 'Ti1 O1 1.9525 .\n')
    assert set(r.sites['element']) == {'Sr', 'Ti'}
    assert 'set aside' in notes(r)


def test_empty_global_block_is_skipped(tmp_path):
    r = run(tmp_path, "data_global\n_journal_name_full 'Test'\n\n" + sno2())
    assert not isinstance(r, list)
    assert r.structure['cif_block'] == 'sno2'
    assert "'global' holds no atom sites" in notes(r)


def test_two_structures_in_one_file_are_both_checked(tmp_path, tin_reference):
    rs = run(tmp_path, sno2() + '\n' + sno2(), name='two.cif')
    assert isinstance(rs, list) and len(rs) == 2
    assert sorted(r.structure['filename'] for r in rs) == [
        'two__sno2.cif', 'two__sno2_2.cif']
    assert all(tin(r) == pytest.approx(tin_reference, abs=1e-3) for r in rs)


def test_one_structure_readable_one_not_both_reported(tmp_path):
    bad = '\n'.join(l for l in sno2().split('\n') if not l.startswith('_cell_'))
    rs = run(tmp_path, sno2() + '\n' + bad.replace('data_sno2', 'data_nocell'))
    assert isinstance(rs, list) and len(rs) == 2
    assert sorted(r.readable for r in rs) == [False, True]
    assert 'no cell' in [r for r in rs if not r.readable][0].evidence


def test_dummy_labels_are_made_unique(tmp_path, tin_reference):
    r = run(tmp_path, sno2(labels=('XX', 'XX')))
    assert tin(r) == pytest.approx(tin_reference, abs=1e-3)
    assert 'renamed XX_1 to XX_2' in notes(r)
    assert 'renamed XX_1 to XX_2' in r.report_html()      # said where it is read


def test_shared_position_under_another_elements_label(tmp_path):
    # Ni under the label 'Mg1': the index took magnesium's sum for it, and
    # post-processing stopped on the disagreement.
    r = run(tmp_path, cif('mgnio', (4.20,) * 3 + (90,) * 3, 'F m -3 m',
                          [('Mg1', 'Mg2+', 0, 0, 0, 0.5), ('Mg1', 'Ni2+', 0, 0, 0, 0.5),
                           ('O1', 'O2-', 0.5, 0.5, 0.5, 1)],
                          [('Mg2+', 2), ('Ni2+', 2), ('O2-', -2)]))
    assert set(r.sites['element']) == {'Mg', 'Ni'}
    assert r.tier == 'ACCEPT_HOMOVALENT'


def test_unquoted_space_group(tmp_path, tin_reference):
    r = run(tmp_path, sno2().replace("'P 42/m n m'", 'P 42/m n m'))
    assert tin(r) == pytest.approx(tin_reference, abs=1e-3)


def test_operations_in_an_untabulated_origin(tmp_path, tin_reference):
    import gemmi
    sh, inv = gemmi.Op('x+1/4,y+1/4,z'), gemmi.Op('x-1/4,y-1/4,z')
    ops = [(inv * o * sh).wrap().triplet()
           for o in gemmi.find_spacegroup_by_name('P 42/m n m').operations()]
    t = (['data_shifted'] + [f'_cell_{k} {v}' for k, v in zip(
        ('length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma'), RUT)]
         + ['loop_', '_symmetry_equiv_pos_as_xyz'] + [f"'{o}'" for o in ops]
         + ['loop_', '_atom_type_symbol', '_atom_type_oxidation_number', 'Sn4+ 4', 'O2- -2',
            'loop_', '_atom_site_label', '_atom_site_type_symbol', '_atom_site_fract_x',
            '_atom_site_fract_y', '_atom_site_fract_z', '_atom_site_occupancy',
            'Sn1 Sn4+ 0.75 0.75 0 1', 'O1 O2- 0.0556 0.0556 0 1'])
    r = run(tmp_path, '\n'.join(t) + '\n')
    assert (r.tier, r.code) == ('ACCEPT', '-')
    assert tin(r) == pytest.approx(tin_reference, abs=1e-3)
    assert 'moved the origin' in notes(r)


def test_carbonate_is_not_expunged_for_its_own_edge(tmp_path):
    r = run(tmp_path, cif('calcite', (4.9896, 4.9896, 17.061, 90, 90, 120), 'R -3 c',
                          [('Ca1', 'Ca2+', 0, 0, 0, 1), ('C1', 'C4+', 0, 0, 0.25, 1),
                           ('O1', 'O2-', 0.2578, 0, 0.25, 1)],
                          [('Ca2+', 2), ('C4+', 4), ('O2-', -2)]))
    assert r.code != 'G2' and r.tier != 'EXPUNGE'
    assert float(r.structure['polyanion_edge_min']) == pytest.approx(2.228, abs=0.02)


def test_hexafluorophosphate_is_not_expunged_for_its_own_edge(tmp_path):
    r = run(tmp_path, cif('napf6', (7.61,) * 3 + (90,) * 3, 'F m -3 m',
                          [('P1', 'P5+', 0, 0, 0, 1), ('Na1', 'Na1+', 0.5, 0.5, 0.5, 1),
                           ('F1', 'F1-', 0.2103, 0, 0, 1)],
                          [('P5+', 5), ('Na1+', 1), ('F1-', -1)]))
    assert r.code != 'G2'
    assert float(r.structure['polyanion_edge_min']) == pytest.approx(2.263, abs=0.02)


def test_molecular_carbon_is_not_assessed_and_says_why(tmp_path):
    t = cif('mapbi3', (6.33,) * 3 + (90,) * 3, 'P 1',
            [('Pb1', 'Pb2+', 0, 0, 0, 1), ('I1', 'I1-', 0.5, 0, 0, 1),
             ('I2', 'I1-', 0, 0.5, 0, 1), ('I3', 'I1-', 0, 0, 0.5, 1),
             ('C1', 'C', 0.383, 0.5, 0.5, 1), ('N1', 'N', 0.617, 0.5, 0.5, 1)])
    r = run(tmp_path, t, ox={'Pb': 2, 'I': -1, 'C': -4, 'N': -3})
    assert (r.tier, r.code, r.reason) == ('NOT_ASSESSED', 'R1', 'molecular_carbon')
    assert 'C1-N1' in r.evidence
    assert 'covalent' in r.verdict().lower()
    assert '<html' in r.report_html().lower()


def test_an_item_given_twice_says_which(tmp_path):
    r = run(tmp_path, sno2().replace('_cell_length_c', '_cell_length_a 4.70\n_cell_length_c'))
    assert not r.readable
    assert '_cell_length_a more than once' in r.evidence


def test_a_template_with_no_atoms_says_so(tmp_path):
    r = run(tmp_path, "# GSAS-II phase information template file\ndata_template\n"
                      "_pd_phase_name ?\n")
    assert not r.readable
    assert 'no data block holds atom sites' in r.evidence


def test_the_copy_as_read_is_kept_and_found(tmp_path):
    (tmp_path / 'a.cif').write_text(sno2(labels=('XX', 'XX')))
    (tmp_path / 'b.cif').write_text(sno2())
    res = eir.check_folder(tmp_path, verbose=False)
    d = tmp_path / 'outputs' / 'as_read'
    assert (d / 'a.cif').exists() and not (d / 'b.cif').exists()
    assert json.loads((d / 'manifest.json').read_text()) == ['a.cif']
    e = eir.engine
    assert e.cif_path_for(tmp_path, 'a.cif') == str(d / 'a.cif')
    assert e.cif_path_for(tmp_path, 'b.cif') == str(tmp_path / 'b.cif')
    assert len(res) == 2
