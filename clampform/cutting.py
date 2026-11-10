"""Cutting forces (Kienzle), surface roughness, power and tool life for single-point turning and grooving.

Kienzle: F_c = k_c1.1 * b * h^(1 - m_c) * K_gamma * K_v * K_wear * K_st      (specific cutting force law; values and
correction factors from the table in data/materials.json, which names its source).

Chip geometry with a nose radius: the cross-section A = a_p * f is spread over the engaged edge length L; the mean
chip thickness is h_m = A / L. The resultant of feed and passive force acts normal to Colwell's equivalent cutting
edge (the chord through the ends of the engaged edge), so for small a_p (finishing) the passive (radial) force
dominates and for large a_p it turns towards the feed direction.

Roughness: the theoretical profile of a round nose is a chain of arcs; Rt = f^2 / (8 r) and Ra = f^2 / (18 sqrt(3) r)
(= 0.0321 f^2 / r). Below a minimum chip thickness the edge ploughs; Brammertz's correction adds
h_min / 2 * (1 + r h_min / f^2) to Rt (Brammertz 1961, quoted from secondary sources). Ra keeps the Ra/Rt ratio of the
arc profile.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .parts import load_json


@dataclass
class Cut:
    Fc: float  # cutting (tangential) force, N
    Ff: float  # feed force, N (along the feed direction)
    Fp: float  # passive force, N (normal to the feed in the reference plane)
    h: float  # mean chip thickness, mm
    kappa_eff: float  # effective entering angle, rad


def _mat(material: str) -> tuple[dict, dict]:
    m = load_json("materials.json")
    return m["kienzle"][material], m


def kc(h: float, material: str, gamma_deg: float, vc: float, kind: str, K_wear: float | None = None,
       kc_scale: float = 1.0) -> float:
    k, m = _mat(material)
    corr = m["corrections"]
    Kg = 1 - (gamma_deg - corr["gamma0_deg"]) / 100
    Kv = 1.03 - 3 * vc / 1e4 if 80 <= vc <= 250 else (100 / vc) ** 0.1
    Kw = corr["K_wear"] if K_wear is None else K_wear
    Kst = corr["K_st"].get(kind, 1.0)
    return kc_scale * k["kc11"] * max(h, 1e-4) ** (-k["mc"]) * Kg * Kv * Kw * Kst


def turning(ap: float, f: float, rn: float, kappa_deg: float, material: str, vc: float, kind: str = "turn",
            gamma_deg: float = 6.0, thrust_ratio: float | None = None, **kw) -> Cut:
    """Longitudinal turning or boring with a nose radius rn (mm)."""
    kap = math.radians(min(kappa_deg, 90.0))
    if ap <= rn * (1 - math.cos(kap)):
        th = math.acos(1 - ap / rn)
        L = rn * th + f / 2
        span = rn * math.sin(th) + f / 2
    else:
        L = rn * kap + (ap - rn * (1 - math.cos(kap))) / math.sin(kap) + f / 2
        span = rn * math.sin(kap) + (ap - rn * (1 - math.cos(kap))) / math.tan(kap) + f / 2
    A = ap * f
    h = A / L
    Fc = kc(h, material, gamma_deg, vc, kind, **kw) * A
    ratio = load_json("materials.json")["force_ratios"]["thrust_over_cutting"] if thrust_ratio is None else thrust_ratio
    ke = math.atan2(ap, span)
    Ft = ratio * Fc
    return Cut(Fc, Ft * math.sin(ke), Ft * math.cos(ke), h, ke)


def plunge(width: float, f: float, material: str, vc: float, kind: str = "groove_int", gamma_deg: float = 0.0,
           thrust_ratio: float | None = None, **kw) -> Cut:
    """Radial plunge with a straight grooving insert: chip width = insert width, chip thickness = radial feed.
    The thrust acts along the feed, i.e. radially on the part."""
    Fc = kc(f, material, gamma_deg, vc, kind, **kw) * width * f
    ratio = load_json("materials.json")["force_ratios"]["thrust_over_cutting"] if thrust_ratio is None else thrust_ratio
    return Cut(Fc, ratio * Fc, 0.0, f, math.pi / 2)


def roughness(f: float, rn: float, h_min: float = 0.002) -> tuple[float, float]:
    """(Ra, Rt) in um for feed f and nose radius rn (mm). h_min: minimum chip thickness (assumed 2 um for a honed carbide edge)."""
    rt = f * f / (8 * rn)
    if h_min > 0:
        rt += h_min / 2 * (1 + rn * h_min / (f * f))
    ra = rt * (8 / (18 * math.sqrt(3)))  # Ra/Rt of the arc profile = 0.257
    return ra * 1e3, rt * 1e3


def feed_for_ra(ra_um: float, rn: float, f_max: float, h_min: float = 0.002) -> float:
    """Largest feed (mm/rev, rounded down to 0.005) whose Ra (with the ploughing term) stays below ra_um.
    With ploughing, Rt has its minimum at f* = sqrt(2 r h_min); above f* Ra rises monotonically with feed."""
    lo, hi = math.sqrt(2 * rn * h_min), f_max
    if roughness(lo, rn, h_min)[0] > ra_um:
        raise ValueError(f"Ra {ra_um} um is below what nose radius {rn} mm can reach")
    if roughness(hi, rn, h_min)[0] <= ra_um:
        return f_max
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if roughness(mid, rn, h_min)[0] <= ra_um:
            lo = mid
        else:
            hi = mid
    return max(math.floor(lo / 0.005) * 0.005, 0.005)


def power_kW(Fc: float, vc: float, eff: float = 0.8) -> float:
    return Fc * vc / 60 / 1e3 / eff


def taylor_life_min(vc: float, vc_ref: float, T_ref: float = 15.0, n: float = 0.25) -> float:
    """Tool life (min) at vc for a tool whose reference speed vc_ref gives T_ref (vc T^n = C)."""
    C = vc_ref * T_ref**n
    return (C / max(vc, 1e-6)) ** (1 / n)


def rpm(vc: float, d: float, n_cap: float) -> float:
    """Spindle speed for constant surface speed vc (m/min) at diameter d (mm), capped (G50 / LIMS)."""
    return min(1000 * vc / (math.pi * max(d, 1e-6)), n_cap)
