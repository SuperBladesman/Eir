"""eir.check on the example structures."""
import pytest

import eir


def test_accept(examples):
    r = eir.check(examples / 'MgO.cif')
    assert r.tier == 'ACCEPT'
    assert r.code == '-'
    name, value, sigma = r.quote
    assert name == 'gii'
    assert 0 < value < 0.2
    assert 'Nothing wrong found' in r.verdict()
    assert any('Source grouping skipped' in n for n in r.run.notes)


def test_failed_screen_is_reported(examples):
    # Only the identity operator: the symmetry is never expanded, every
    # cation is under-coordinated, and no gate reads the coordination screen.
    p = examples / 'SrTiO3_refined.cif'
    p.write_text(p.read_text().replace(
        '_space_group_IT_number 221\n',
        '_space_group_IT_number 221\nloop_\n_space_group_symop_operation_xyz\n'
        'x,y,z\n'))
    r = eir.check(p, oxidation_states={'Sr': 2, 'Ti': 4, 'O': -2})
    x = r.explanation()
    assert 'coordination' in x['failed_screens']
    assert x['screen_note'] and 'coordination' in x['screen_note']


def test_oxidation_states_from_argument(examples):
    r = eir.check(examples / 'SrTiO3_refined.cif',
                  oxidation_states={'Sr': 2, 'Ti': 4, 'O': -2})
    assert r.tier == 'ACCEPT'
    assert set(r.sites['element']) == {'Sr', 'Ti'}


def test_oxidation_states_needed(examples):
    with pytest.raises(eir.OxidationStatesNeeded) as err:
        eir.check(examples / 'SrTiO3_refined.cif')
    assert set(err.value.elements) == {'Sr', 'Ti'}


def test_config_json_beside_the_cif(examples):
    (examples / 'config.json').write_text('{"Sr": 2, "Ti": 4, "O": -2}')
    r = eir.check(examples / 'SrTiO3_refined.cif')
    assert r.tier == 'ACCEPT'


def test_expunge(examples):
    r = eir.check(examples / 'MgO_wrong_cell.cif')
    assert r.tier == 'EXPUNGE'
    assert r.code == 'G6'
    assert r.reason == 'contact_below_measured_minimum'
    x = r.explanation()
    assert x['quote']['status'] == 'withheld'
    assert 'Do not quote' in r.verdict()


def test_unreadable(tmp_path):
    p = tmp_path / 'broken.cif'
    p.write_text('data_broken\n_cell_length_a 5.0\nthis is not a cif\n')
    r = eir.check(p)
    assert not r.readable
    assert r.tier == 'EXPUNGE'
    assert 'could not read' in r.verdict()


def test_repeat_runs_agree(examples):
    a = eir.check(examples / 'MgO_wrong_cell.cif')
    eir.check(examples / 'MgO.cif')
    b = eir.check(examples / 'MgO_wrong_cell.cif')
    assert a.sites.equals(b.sites)


def test_missing_file(tmp_path):
    with pytest.raises(eir.EirError):
        eir.check(tmp_path / 'nope.cif')


def test_keep_outputs(examples, tmp_path):
    out = tmp_path / 'kept'
    eir.check(examples / 'MgO.cif', output_dir=out)
    assert list(out.glob('eir_batch_results_*_quality.csv'))
    assert list(out.glob('eir_batch_results_*_structures.csv'))
