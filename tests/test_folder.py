"""eir.check_folder: the notebook's pipeline on a folder."""
import eir


def test_folder(examples):
    res = eir.check_folder(examples, verbose=False, reports=True,
                           oxidation_states={'Mg': 2, 'Sr': 2, 'Ti': 4,
                                             'O': -2})
    assert len(res) == 3
    tiers = dict(zip(res.structures['filename'],
                     res.structures['structure_pgrm_tier']))
    assert tiers['MgO.cif'] == 'ACCEPT'
    assert tiers['MgO_wrong_cell.cif'] == 'EXPUNGE'
    assert tiers['SrTiO3_refined.cif'] == 'ACCEPT'
    out = examples / 'outputs'
    assert (out / 'eir_summary.txt').exists()
    assert list(out.glob('eir_batch_results_*_structures.csv'))
    assert len(list((out / 'reports').glob('*.eir.html'))) == 3
    assert {r.tier for r in res.results()} == {'ACCEPT', 'EXPUNGE'}
    # None of the examples has an ICSD code, where engine 2.0.45 stops in
    # flag_same_source_entries; the package finishes and says so.
    assert any('Source grouping skipped' in n for n in res.notes)
