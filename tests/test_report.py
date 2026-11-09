"""The one-page report."""
import eir


def test_report_expunge(examples, tmp_path):
    r = eir.check(examples / 'MgO_wrong_cell.cif')
    p = r.write_report(tmp_path / 'r.html')
    html = p.read_text(encoding='utf-8')
    assert html.startswith('<!doctype html>')
    assert 'Cannot be right' in html
    assert 'contact_below_measured_minimum' in html
    assert 'data:image/png;base64,' in html          # a polyhedron was drawn
    assert 'Geometry screens' in html
    assert 'engine ' + eir.ENGINE_VERSION in html


def test_report_default_path(examples):
    r = eir.check(examples / 'MgO.cif')
    p = r.write_report()
    assert p == examples / 'MgO.eir.html'
    assert 'Nothing wrong found' in p.read_text(encoding='utf-8')


def test_report_unreadable(tmp_path):
    cif = tmp_path / 'broken.cif'
    cif.write_text('data_broken\nnot a cif\n')
    html = eir.check(cif).report_html()
    assert 'could not read' in html


def test_notebook_fragment(examples):
    r = eir.check(examples / 'MgO.cif')
    frag = r._repr_html_()
    assert frag.startswith('<div class="eir-report">')
    assert ':root' not in frag
