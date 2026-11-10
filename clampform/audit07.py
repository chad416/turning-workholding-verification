"""Audit of the lathe programs written by the part-family generator (project 07) for the same parts.

07 checks geometry: it reads its G-code back into a material-removal simulation. It does not know the chuck. Its
programs start every tool with `G50 S3500` (the lathe's maximum) and face the solid bar to X0 under G96, so the
spindle runs up to the G50 limit at the end of every facing cut. This module asks what that does to the grip:

  * the static force a set-up needs for the program's own roughing and drilling (VDI method, clamp.py);
  * the centrifugal loss of the jaws at the program's G50 speed;
  * whether the grip at that speed still meets S_z, and the highest speed at which it would.

The programs are read as text (regex on the stock comment, G50, G96 and the G71 roughing parameters); 07 is not
imported or changed. The program files are copies of the outputs in project 13 (reports/cnc), which ran 07.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

from . import clamp as clp
from . import cutting as ct
from .parts import DATA, load_json


@dataclass
class Audit:
    program: str
    stock_d: float
    g50: float
    faces_to_centre: bool
    F_set: float  # static force the program's heaviest cut needs (VDI method), N
    governing_cut: str
    chuck: str
    F_cent_at_g50: float  # centrifugal loss at the G50 speed, N
    F_residual: float  # F_set - F_c(G50): what still holds the bar at the end of the facing cut
    n_allow_face: float  # highest speed at which F_set still meets the VDI requirement with no cut (F_c <= F_set / S_sp)
    jaw_mr_ratio: float  # sum m r of the soft jaws / sum m r implied by the chuck rating (2/3 F_max lost at n_max)


def _drill_torque_Nm(d: float, f: float, material: str) -> float:
    """Kienzle for drilling: two edges, chip width d/2, chip thickness f/2 (point angle ignored):
    M = kc(f/2) * f * d^2 / 8."""
    k = ct.kc(f / 2, material, 6.0, 100.0, "bore")
    return k * f * d * d / 8 / 1e3


def rated_mr(ch: clp.Chuck) -> float:
    """Jaw sum(m r) (kg mm, all jaws) implied by the rating rule that at n_max the clamping force has fallen to
    1/3 of F_max with the maker's standard jaws (EN 1550 / VDI 3106 rating practice, quoted from memory)."""
    w = 2 * math.pi * ch.n_max / 60
    return (2 / 3) * ch.F_max / (w * w) * 1e3


def audit_program(path: Path, material: str = "C45") -> Audit:
    text = path.read_text(encoding="utf-8")
    stock = float(re.search(r"STOCK D([\d.]+)", text).group(1))
    g50 = max(float(v) for v in re.findall(r"G50 S(\d+)", text))
    faces = bool(re.search(r"G96 S\d+ M3[\s\S]*?G1 X0\.000 Z0\.\d+", text))
    m = re.search(r"G71 U([\d.]+) R[\d.]+\nG71 P\d+ Q\d+ U[\d.]+ W[\d.]+ F([\d.]+)", text)
    ap, f = (float(m.group(1)), float(m.group(2))) if m else (2.0, 0.25)
    vc = float(re.search(r"G96 S(\d+)", text).group(1))
    T = load_json("tools.json")["tools"]["T01"]
    ch = clp.chucks()[f"3J-{'315' if stock > 120 else '210'}"]
    cut = ct.turning(ap, f, T["rn"], T["kappa_deg"], material, vc)
    r_g = stock / 2
    cands = [("OD roughing", cut.Fc * (stock / 2 - ap / 2) / r_g, ct.rpm(vc, stock, min(g50, ch.n_max)))]
    for d, n, fd in re.findall(r"INSERT DRILL D(\d+)\)\nG97 S(\d+) M3[\s\S]*?F([\d.]+)", text):
        Mt = _drill_torque_Nm(float(d), float(fd), material)
        cands.append((f"drilling D{d}", Mt * 1e3 / r_g, float(n)))
    name, F = max(((nm, clp.required_static(Ft, ch.centrifugal(n, stock))) for nm, Ft, n in cands), key=lambda t: t[1])
    F = min(F, ch.F_max)
    Fc = ch.centrifugal(g50, stock)
    S_sp = clp.factors()["S_sp"]
    per = ch.centrifugal(60 / (2 * math.pi), stock)
    n_allow = min(math.sqrt(F / S_sp / per) * 60 / (2 * math.pi), ch.n_max)
    mr = ch.n_jaws * (ch.m_top * (stock / 2 + ch.top_offset) + ch.m_base * ch.r_base)
    return Audit(path.stem, stock, g50, faces, F, name, ch.name, Fc, F - Fc, n_allow, mr / rated_mr(ch))


def audit_all() -> list[Audit]:
    return [audit_program(p) for p in sorted((DATA / "p07").glob("*.nc"))]


def facing_end_speed(vc: float, g50: float, d_end: float = 0.0) -> float:
    """Speed at the end of a G96 facing cut to d_end: capped by G50 (d_end = 0 always reaches the cap)."""
    return g50 if d_end <= 1000 * vc / (math.pi * g50) else 1000 * vc / (math.pi * d_end)
