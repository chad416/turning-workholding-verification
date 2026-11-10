"""The findings the dossier relies on, and the program writer / read-back verifier."""

import re

import pytest

from clampform import gcode
from clampform.audit07 import audit_all
from clampform.form import PartFE
from clampform.parts import load_parts
from clampform.process import chuck_for, evaluate
from clampform.verify import verify

P = load_parts()


@pytest.fixture(scope="module")
def tube_ld():
    p = P["TU-LD-80C"]
    return p, PartFE(p, chuck_for(p, "3J").grip_len)


@pytest.fixture(scope="module")
def piston_ld():
    p = P["PI-LD-80C"]
    return p, PartFE(p, chuck_for(p, "3J").grip_len)


def test_thin_tube_one_pressure_is_out_of_round_and_two_point_gauge_cannot_see_it(tube_ld):
    p, fe = tube_ld
    r = evaluate(p, fe, "3J", "single")
    f = r.features[0]
    assert f.ron_um > 3 * f.budget_um  # several times the H8 budget
    assert f.two_point_um < 0.1 * f.ron_um  # the 3-lobe shape keeps a constant two-point size
    assert f.v108_um > 2 * f.ron_um  # a 108 deg vee shows it amplified


def test_thin_tube_two_stage_is_limited_by_the_chuck_minimum_not_by_the_cut(tube_ld):
    p, fe = tube_ld
    r = evaluate(p, fe, "3J", "two-stage")
    assert any("chuck minimum" in n for n in r.notes)
    assert not r.features[0].ok  # still over budget at the minimum force


def test_six_jaws_fix_the_thin_tube_at_one_pressure(tube_ld):
    p, fe = tube_ld
    r = evaluate(p, fe, "6J", "single")
    assert r.features[0].ok and r.features[0].ron_um < 0.3 * r.features[0].budget_um


def test_bar_work_piston_is_round_with_a_plain_three_jaw_chuck(piston_ld):
    p, fe = piston_ld
    r = evaluate(p, fe, "3J", "single")
    assert all(f.ok for f in r.features)
    assert r.min_grip >= 1.5


def test_generated_program_passes_the_read_back(piston_ld):
    p, fe = piston_ld
    r = evaluate(p, fe, "3J", "two-stage")
    for dialect in ("fanuc", "sinumerik"):
        res = verify(gcode.write(p, r, dialect), p, "3J", fe)
        assert res.ok, [(f.rule, f.line, f.msg) for f in res.findings]
        assert res.min_grip >= 1.5
        # the verifier recomputes the finishing force from the text; it must agree with the planner
        for f in r.features:
            assert res.feature_force[f.feature.name] == pytest.approx(f.F_cut, rel=0.02)


def test_verifier_catches_unsafe_edits(piston_ld):
    p, fe = piston_ld
    r = evaluate(p, fe, "3J", "two-stage")
    txt = gcode.write(p, r, "fanuc")
    # preset switched while the spindle turns
    bad = txt.replace("M5\nM62", "M62", 1)
    assert any(f.rule == "W3" for f in verify(bad, p, "3J").findings)
    # dwell at the groove bottom removed
    bad = re.sub(r"\nG4 X0\.\d+", "", txt, count=1)
    assert any(f.rule == "W4" for f in verify(bad, p, "3J").findings)
    # speed limit removed before G96
    bad = txt.replace("G50 S", "(G50 REMOVED) S", 1)
    bad = re.sub(r"\n\(G50 REMOVED\) S\d+", "", bad)
    assert any(f.rule == "W2" for f in verify(bad, p, "3J").findings)
    # low preset lowered below what the finishing cuts need
    bad = re.sub(r"LOW [\d.]+ KN", "LOW 0.5 KN", txt)
    assert any(f.rule in ("W1", "W5") for f in verify(bad, p, "3J").findings)


def test_generic_g50_s3500_lets_the_large_chuck_open_while_facing_to_centre():
    A = {a.program: a for a in audit_all()}
    hd, ld = A["GL-HD-160-revB"], A["GL-LD-80-revC"]
    assert hd.faces_to_centre and hd.g50 == 3500
    assert hd.F_residual < 0  # jaw centrifugal force exceeds the force set for the program's own cuts
    assert hd.n_allow_face < 2100
    assert hd.jaw_mr_ratio > 1.2  # soft jaws heavier than the rating assumes
    assert ld.F_residual > 0 and ld.n_allow_face >= 3500 - 1
