"""Each model against an independent closed form or a hand calculation."""

import math

import numpy as np
import pytest

from clampform import clamp as clp
from clampform import cutting as ct
from clampform.form import THETA, two_point_reading, vblock_reading
from clampform.harmfe import HarmonicModel, build_mesh, jaw_harmonics
from clampform.parts import _BANDS, _LOWER, it_grade, limits
from clampform.ring import ring_w, roark_two_point_dD

E = 210e3


def _ring_fe(n, alpha, R=50.0, t=2.0, b=10.0, P=1.0):
    M = HarmonicModel(build_mesh([(R - t / 2, R + t / 2, 0, b)], 0.5), E, 0.0)
    ro = R + t / 2
    th = np.array([0.0, math.pi / n])
    nn = M.nodes_on(R, 0, b)
    ur = np.zeros(2)
    for k, c in jaw_harmonics(n, alpha, 90):
        u = M.solve(k, M.surface_load(k, ro, 0, b, -P * c / (ro * b)))
        ur += u[nn, 0].mean() * np.cos(k * th)
    return -ur, ring_w(th, n, P, R, E, b, t, alpha)


@pytest.mark.parametrize("n,alpha", [(2, 0.02), (3, 0.02), (3, math.radians(50)), (6, 0.02)])
def test_harmonic_fe_matches_thin_ring_theory(n, alpha):
    fe, ring = _ring_fe(n, alpha)
    # thin-ring theory leaves out shear and through-thickness strain; their share grows with k t / R (1.5 % at k = 6)
    assert np.allclose(fe, ring, rtol=0.005 if n < 6 else 0.02), (fe, ring)


def test_ring_series_reproduces_roark_two_point_load():
    R, b, t, P = 50.0, 10.0, 2.0, 100.0
    I = b * t**3 / 12
    # bending-only series: 2 * sum_m (2P/(pi R)) R^4 / (EI (4m^2-1)^2)
    dD = 2 * sum(2 * P / (math.pi * R) * R**4 / (E * I * (4 * m * m - 1) ** 2) for m in range(1, 400))
    assert dD == pytest.approx(roark_two_point_dD(P, R, E, I), rel=1e-4)
    assert roark_two_point_dD(1, 1, 1, 1) == pytest.approx(0.1488, abs=1e-4)


def test_harmonic_fe_k0_matches_lame_external_pressure():
    a, b_, L, p = 40.0, 50.0, 400.0, 10.0
    M = HarmonicModel(build_mesh([(a, b_, 0, L)], 2.0), E, 0.3)
    u = M.solve(0, M.surface_load(0, b_, 0, L, -p))
    nn = M.nodes_on(a, L / 2 - 1, L / 2 + 1)
    u_lame = -2 * p * b_**2 * a / (E * (b_**2 - a**2))  # open ends, radial displacement of the bore
    assert u[nn, 0].mean() == pytest.approx(u_lame, rel=0.01)


def test_jaw_fourier_series_rebuilds_the_jaw_pressure():
    n, alpha = 3, math.radians(20)
    p = sum(c * np.cos(k * THETA) for k, c in jaw_harmonics(n, alpha, 3000))
    inside = np.abs(((THETA + math.pi / 3) % (2 * math.pi / 3)) - math.pi / 3) < alpha * 0.8
    outside = np.abs(((THETA + math.pi / 3) % (2 * math.pi / 3)) - math.pi / 3) > alpha * 1.2
    assert np.allclose(p[inside], 1 / (2 * alpha), rtol=0.05)  # unit force over an arc 2 alpha
    assert np.allclose(p[outside], 0, atol=0.05 / (2 * alpha))


@pytest.mark.parametrize("k,angle,expected", [(3, 108, 1 - math.cos(3 * math.radians(54)) / math.cos(math.radians(54))),
                                              (5, 60, 2.0), (3, 120, 3.0), (2, 90, 1.0)])
def test_vblock_sensitivity_matches_kinematics(k, angle, expected):
    dev = np.cos(k * THETA)  # RONt = 2
    assert vblock_reading(dev, angle) / 2 == pytest.approx(abs(expected), rel=0.01)


def test_two_point_gauge_is_blind_to_odd_lobes():
    assert two_point_reading(np.cos(3 * THETA)) == pytest.approx(0, abs=1e-9)
    assert two_point_reading(np.cos(2 * THETA)) == pytest.approx(4.0, rel=1e-3)  # sees twice the RONt


def test_iso286_table_against_tolerance_unit_formula():
    for up, it, _ in _BANDS:
        D = math.sqrt(up * _LOWER[up])
        i = 0.45 * D ** (1 / 3) + 0.001 * D
        for g, mult in ((7, 16), (8, 25), (9, 40), (11, 100)):
            assert it[g] == pytest.approx(mult * i, rel=0.04)
    assert limits(80, "f7") == (-60.0, -30.0)
    assert limits(84, "H8") == (0.0, 54.0)
    assert it_grade(166, 8) == 63


def test_kienzle_force_and_roughness_closed_forms():
    # large depth, sharp nose: h = f sin(kappa), b = ap / sin(kappa) -> Fc = kc11 b h^(1-mc) * K
    c = ct.turning(4.0, 0.3, 1e-6, 90, "C45", 100.0, gamma_deg=6.0, K_wear=1.0)
    K_v = 1.03 - 3 * 100 / 1e4
    assert c.Fc == pytest.approx(2110 * 4.0 * 0.3 ** (1 - 0.17) * K_v, rel=0.01)
    ra, rt = ct.roughness(0.2, 0.8, h_min=0)
    assert rt == pytest.approx(0.2**2 / (8 * 0.8) * 1e3)
    assert ra == pytest.approx(0.2**2 / (18 * math.sqrt(3) * 0.8) * 1e3)
    # finishing (ap < r): the passive force dominates the thrust
    fin = ct.turning(0.2, 0.1, 0.8, 93, "C45", 200.0)
    assert fin.Fp > 2 * fin.Ff


def test_centrifugal_force_and_speed_limit_are_consistent():
    ch = clp.chucks()["3J-315"]
    n, d = 1500.0, 165.0
    w = 2 * math.pi * n / 60
    hand = 3 * (1.40 * (82.5 + 25) + 1.20 * 95) * 1e-3 * w * w
    assert ch.centrifugal(n, d) == pytest.approx(hand)
    F, Ft = 60e3, 1000.0
    nl = clp.speed_limit(ch, F, Ft, d)
    assert clp.required_static(Ft, ch.centrifugal(nl, d)) == pytest.approx(F, rel=1e-6)
