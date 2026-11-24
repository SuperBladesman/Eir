"""Gagné's bond-length table (Data/gagne_bond_lengths.json).

Each entry's sample size counts coordination polyhedra; the bonds are that
number times the coordination number. Until 2.0.49 the field was called
n_bonds, and references c and d were each other's (#51). Summed by source,
the counts give each paper's published totals, which is how both were found.
"""
import json
from collections import defaultdict
from pathlib import Path

import pytest

import eir

DATA = Path(__file__).resolve().parents[1] / 'Data'

GROUPS = {
    'alkali': {'Li', 'Na', 'K', 'Rb', 'Cs'},
    'alkaline earth': {'Be', 'Mg', 'Ca', 'Sr', 'Ba'},
    'lanthanides': {'La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',
                    'Ho', 'Er', 'Tm', 'Yb', 'Lu'},
    'actinides': {'Th', 'U', 'Np', 'Am', 'Cm'},
    'hydrogen': {'H'},
    'groups 14-16': {'C', 'N', 'P', 'S', 'Se'},
    'group 17': {'Cl', 'Br', 'I'},
    'metalloids': {'B', 'Si', 'Ge', 'As', 'Sb', 'Te'},
    'post-transition': {'Al', 'Ga', 'In', 'Tl', 'Sn', 'Pb', 'Bi'},
}

# (source, group): (coordination polyhedra, bonds) as each paper's abstract
# gives them. Gagné & Hawthorne (2016) Acta Cryst. B72, 602; Gagné (2018)
# Acta Cryst. B74, 49; Gagné & Hawthorne (2018) Acta Cryst. B74, 79 (c) and
# 63 (d), whose text gives 5826 polyhedra for groups 14-16 where its
# abstract gives 5957; Gagné (2021) Chem. Sci. 12, 4599, as counted by
# Hawthorne & Gagné (2024) Acta Cryst. B80. Gagné & Hawthorne (2020) IUCrJ 7,
# 581 gives 7522 and 41 488 for the transition metals, where the table sums
# to 7523 and 41 494 (one six-coordinate polyhedron more), so they are left
# out.
PUBLISHED = {
    ('a', 'alkali'): (4859, 38594),
    ('a', 'alkaline earth'): (3038, 24487),
    ('b', 'lanthanides'): (1317, 10700),
    ('b', 'actinides'): (671, 4754),
    ('c', 'hydrogen'): (223, 452),
    ('c', 'groups 14-16'): (5826, 22784),
    ('c', 'group 17'): (248, 1394),
    ('d', 'metalloids'): (5279, 21761),
    ('d', 'post-transition'): (1821, 10723),
    ('f', 'nitrides'): (875, 4048),
}


@pytest.fixture(scope='module')
def table():
    return json.loads((DATA / 'gagne_bond_lengths.json').read_text(
        encoding='utf-8'))


def entries(table):
    for el, vs in table.items():
        if el.startswith('_'):
            continue
        for v, by_anion in vs.items():
            for anion, by_cn in by_anion.items():
                for cn, rec in by_cn.items():
                    yield el, int(v), anion, int(cn), rec


def group_of(el, ref):
    if ref == 'f':
        return 'nitrides'
    if ref == 'e':
        return 'transition metals'
    return next(g for g, s in GROUPS.items() if el in s)


def test_every_entry_counts_polyhedra(table):
    recs = [rec for *_, rec in entries(table)]
    assert len(recs) == 596
    assert not [r for r in recs if 'n_bonds' in r]
    assert all(isinstance(r['n_polyhedra'], int) and r['n_polyhedra'] > 0
               for r in recs)
    assert 'n_polyhedra' in table['_metadata']['fields']


def test_the_counts_add_up_to_each_papers_totals(table):
    poly, bonds = defaultdict(int), defaultdict(int)
    for el, v, anion, cn, rec in entries(table):
        key = (rec['ref'], group_of(el, rec['ref']))
        poly[key] += rec['n_polyhedra']
        bonds[key] += rec['n_polyhedra'] * cn
    for key, (p, b) in PUBLISHED.items():
        assert (poly[key], bonds[key]) == (p, b), key


def test_each_reference_holds_its_own_paper(table):
    refs = table['_metadata']['references']
    assert 'Non-metals' in refs['c'] and 'B74, 79-96' in refs['c']
    assert 'Metalloids' in refs['d'] and 'B74, 63-78' in refs['d']
    for el, v, anion, cn, rec in entries(table):
        g = group_of(el, rec['ref'])
        if rec['ref'] == 'c':
            assert g in ('hydrogen', 'groups 14-16', 'group 17'), el
        if rec['ref'] == 'd':
            assert g in ('metalloids', 'post-transition'), el
        if rec['ref'] == 'e':
            assert el not in GROUPS['post-transition'], (el, v, cn)


def test_g6_states_its_sample_in_polyhedra():
    e = eir.engine
    row = {'element': 'Fe', 'valence': 3, 'cn': 4, 'min_bond_length': 1.5,
           'coords': '(0.125, 0.125, 0.125)',
           'bl_ratio_min': 0.80, 'bl_n_polyhedra': 65, 'bl_tier': 1,
           'bl_expected_min': 1.83, 'contact_above_floor': True}
    code, reason, evidence = e.classify_site(row, {})
    assert code == 'G6', (code, evidence)
    assert evidence.endswith('over 65 polyhedra, a ratio of 0.800'), evidence


def test_output_written_before_the_rename_still_gates():
    # Re-classifying a 2.0.48 table, whose column is bl_n_bonds, must not
    # switch G6 off for want of a sample size.
    e = eir.engine
    row = {'element': 'Fe', 'valence': 3, 'cn': 4, 'min_bond_length': 1.5,
           'coords': '(0.125, 0.125, 0.125)',
           'bl_ratio_min': 0.80, 'bl_n_bonds': 65, 'bl_tier': 1,
           'bl_expected_min': 1.83, 'contact_above_floor': True}
    code, reason, evidence = e.classify_site(row, {})
    assert code == 'G6', (code, evidence)
