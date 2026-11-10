"""Power-chuck clamping force: what the cut needs, what centrifugal force takes away, what the part feels.

Method after VDI 3106 (permissible speed of lathe chucks), as recalled (not re-checked against the guideline):

    F_spz = S_z * F_transfer / mu                    clamping force the cut needs (S_z: cutting-force safety factor)
    F_sp0 = S_sp * (F_spz + F_c(n))                  static (standstill) force to set, OD clamping
    F_c(n) = sum_jaws m_j r_j omega^2                centrifugal force of the jaws, which unloads an OD grip
    F_cut(n) = F_sp0 - F_c(n)                        force that actually squeezes the part while it is cut

F_transfer combines the cutting torque, converted to a tangential force at the grip radius, and the tilting moment
of the lateral cutting force about the grip, converted with the mean lever of n jaws (2/pi of the grip radius;
derived here, conservative because it adds both linearly).

What deforms the part during a cut is F_cut, not F_sp0: the centrifugal loss is a safety problem (the part can
slip or be thrown) but it also relieves the squeeze. The roundness model therefore uses F_cut.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .parts import load_json


@dataclass
class Chuck:
    name: str
    n_jaws: int
    half_angle: float  # rad
    F_max: float  # N
    F_min: float  # N
    n_max: float  # rpm
    grip_len: float
    m_top: float
    top_offset: float
    m_base: float
    r_base: float
    max_grip_d: float
    setup_min: float
    invest_rel: float

    def centrifugal(self, n_rpm: float, grip_d: float) -> float:
        w = 2 * math.pi * n_rpm / 60
        mr = self.m_top * (grip_d / 2 + self.top_offset) + self.m_base * self.r_base  # kg mm
        return self.n_jaws * mr * 1e-3 * w * w


def chucks() -> dict[str, Chuck]:
    m = load_json("machine.json")["chucks"]
    out = {}
    for k, v in m.items():
        out[k] = Chuck(k, v["n_jaws"], math.radians(v["half_angle_deg"]), v["F_max_kN"] * 1e3, v["F_min_frac"] * v["F_max_kN"] * 1e3,
                       v["n_max_rpm"], v["grip_len"], v["m_top_kg"], v["top_offset_mm"], v["m_base_kg"], v["r_base_mm"],
                       v["max_grip_d"], v["setup_min"], v["invest_rel"])
    return out


def factors() -> dict:
    return load_json("machine.json")["clamping"]


def transfer_force(Fc: float, F_lat: float, r_cut: float, r_grip: float, lever: float) -> float:
    """Tangential-equivalent force at the grip (N): torque Fc*r_cut and tilting moment F_lat*lever."""
    return Fc * r_cut / r_grip + F_lat * lever / (r_grip * 2 / math.pi)


def required_static(F_transfer: float, Fcent: float, mu: float | None = None, S_z: float | None = None,
                    S_sp: float | None = None) -> float:
    f = factors()
    mu = f["mu"] if mu is None else mu
    S_z = f["S_z"] if S_z is None else S_z
    S_sp = f["S_sp"] if S_sp is None else S_sp
    return S_sp * (S_z * F_transfer / mu + Fcent)


def grip_margin(F_sp0: float, Fcent: float, F_transfer: float, mu: float | None = None) -> float:
    """Friction capacity / transferred force at speed (>= 1 holds; the requirement asks >= S_z)."""
    mu = factors()["mu"] if mu is None else mu
    return mu * max(F_sp0 - Fcent, 0.0) / max(F_transfer, 1e-9)


def speed_limit(ch: Chuck, F_sp0: float, F_transfer: float, grip_d: float, mu: float | None = None,
                S_z: float | None = None, S_sp: float | None = None) -> float:
    """Highest spindle speed (rpm) at which F_sp0 still satisfies the VDI-style requirement for this cut."""
    f = factors()
    mu = f["mu"] if mu is None else mu
    S_z = f["S_z"] if S_z is None else S_z
    S_sp = f["S_sp"] if S_sp is None else S_sp
    allowed_cent = F_sp0 / S_sp - S_z * F_transfer / mu
    if allowed_cent <= 0:
        return 0.0
    per = ch.centrifugal(60 / (2 * math.pi), grip_d)  # F_c at omega = 1 rad/s
    return min(math.sqrt(allowed_cent / per) * 60 / (2 * math.pi), ch.n_max)
