"""Run everything for one part: FE, the six workholding strategies, trade study, requirements, FMEA, sensitivity,
the program for the chosen strategy and its read-back verification."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import aoa, fmea, gcode, requirements
from .form import PartFE, metrics
from .parts import Part, load_parts
from .process import StrategyResult, chuck_for, evaluate
from .verify import VerifyResult, verify

STRATS = [("3J", "single"), ("3J", "two-stage"), ("6J", "single"), ("6J", "two-stage"), ("PIE", "single"), ("PIE", "two-stage")]
SENS = [  # label, low override, high override
    ("jaw friction mu 0.08 / 0.20", {"mu": 0.08}, {"mu": 0.20}),
    ("specific cutting force -16 % / +18 %", {"kc_scale": 1780 / 2110}, {"kc_scale": 2500 / 2110}),
    ("thrust / cutting force 0.3 / 0.8", {"thrust_ratio": 0.3}, {"thrust_ratio": 0.8}),
    ("tool wear factor 1.0 / 1.5", {"K_wear": 1.0}, {"K_wear": 1.5}),
    ("top-jaw mass x0.7 / x1.3", {"mass_scale": 0.7}, {"mass_scale": 1.3}),
    ("chuck minimum force 4 % / 12 % of max", {"fmin_frac": 0.04}, {"fmin_frac": 0.12}),
]


@dataclass
class PartResult:
    part: Part
    fe: PartFE
    strategies: list[StrategyResult]
    aoa: dict
    chosen: StrategyResult
    baseline: StrategyResult
    req_base: dict
    req_chosen: dict
    fmea_base: list[dict]
    fmea_chosen: list[dict]
    sens: list[tuple[str, float, float]] = field(default_factory=list)
    sens_base: float = 0.0
    programs: dict[str, str] = field(default_factory=dict)
    verified: dict[str, VerifyResult] = field(default_factory=dict)
    decay: tuple[np.ndarray, np.ndarray] | None = None


def decay_curve(p: Part, fe: PartFE, n_jaws: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """RONt per 10 kN along the bore (final section) against the distance from the jaw edge, measured away from
    the jaws: into the tube body for a tube, towards the part for bar work."""
    M = fe.models["fin"]
    X = M.mesh.nodes
    r = p.bore / 2
    zg0, zg1 = fe.grip_z
    on = np.abs(X[:, 0] - r) < 1e-6
    if p.is_tube:
        nn = np.where(on & (X[:, 1] <= zg0 + 1e-6))[0]
        dist = zg0 - X[nn, 1]
    else:
        nn = np.where(on & (X[:, 1] >= zg1 - 1e-6) & (X[:, 1] <= 1e-6))[0]
        dist = X[nn, 1] - zg1
    order = np.argsort(dist)
    nn, dist = nn[order], dist[order]
    ch = chuck_for(p, "3J")
    u = fe.clamp_response("fin", n_jaws, ch.half_angle, nn) * (10e3 / n_jaws)
    ron = np.array([metrics(r - ui, r).ron for ui in u]) * 1e3
    return dist, ron


def run_part(pid: str, with_programs: bool = True, with_sens: bool = True) -> PartResult:
    p = load_parts()[pid]
    fe = PartFE(p, chuck_for(p, "3J").grip_len)
    res = [evaluate(p, fe, ck, sc) for ck, sc in STRATS]
    sc = aoa.score(res)
    names = [f"{r.chuck} {r.scheme}" for r in res]
    chosen = res[names.index(sc["ranking"][0][0])] if sc["ranking"] else res[1]
    base = res[0]
    pr = PartResult(p, fe, res, sc, chosen, base, requirements.status(base), requirements.status(chosen),
                    fmea.rows(base, p.is_tube), fmea.rows(chosen, p.is_tube))
    if with_sens:
        # sensitivity of the deciding quantity: worst roundness / budget of the 3-jaw two-stage strategy
        ref = res[1]
        pr.sens_base = ref.worst_ron_ratio
        for lab, lo, hi in SENS:
            a = evaluate(p, fe, "3J", "two-stage", sens=dict(lo, tool_defl=False)).worst_ron_ratio
            b = evaluate(p, fe, "3J", "two-stage", sens=dict(hi, tool_defl=False)).worst_ron_ratio
            pr.sens.append((lab, a, b))
    if with_programs:
        kind = chosen.chuck.split("-")[0]
        for dialect in ("fanuc", "sinumerik"):
            txt = gcode.write(p, chosen, dialect)
            pr.programs[dialect] = txt
            pr.verified[dialect] = verify(txt, p, kind, fe)
    pr.decay = decay_curve(p, fe)
    return pr
