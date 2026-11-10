"""Workholding requirements (Wasson ch. 19-22: subject, shall, bound, source, verification method) and their status
for an evaluated strategy. Methods: I inspection, A analysis, D demonstration, T test (Wasson Principle 13.10)."""

from __future__ import annotations

from .process import StrategyResult

REQS = [
    ("R-01", "Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs", "VDI 3106 clamping-force method", "A; T"),
    ("R-02", "The static clamping force set on the chuck shall lie within the chuck's range", "chuck data", "I"),
    ("R-03", "The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating", "VDI 3106; EN 1550 rating", "A; I"),
    ("R-04", "Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle)", "ISO 14405-1 envelope on fits, machined at mid tolerance (derived)", "A; T"),
    ("R-05", "Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um", "seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice", "A; T"),
    ("R-06", "The clamping stress shall stay below Re / 1.5 in the gripped section", "project rule: no permanent set or jaw marks", "A"),
    ("R-07", "The inspection method shall see the lobing order the chuck produces", "ISO 12181 (roundness), derived", "I"),
    ("R-08", "Cutting power shall not exceed the spindle power", "machine data", "A"),
]


def status(r: StrategyResult) -> dict[str, tuple[str, str]]:
    out = {}
    out["R-01"] = ("met" if r.min_grip >= 1.5 - 1e-6 else "NOT met", f"min grip {r.min_grip:.2f}")
    out["R-02"] = ("met" if r.feasible else "NOT met", f"{r.F_high/1e3:.1f} / {r.F_low/1e3:.1f} kN")
    out["R-03"] = ("met", f"G50 {r.g50_high:.0f} / {r.g50_low:.0f} rpm") if r.min_grip >= 1.5 - 1e-6 else ("NOT met", "speed limit too high")
    worst = max((f for f in r.features if f.budget_um), key=lambda f: f.ron_um / f.budget_um, default=None)
    if worst is not None:
        out["R-04"] = ("met" if worst.ok else "NOT met", f"{worst.feature.name}: {worst.ron_um:.1f} / {worst.budget_um:.0f} um")
    ra_bad = [f.feature.name for f in r.features if f.ra_um > f.feature.ra_um + 1e-9]
    out["R-05"] = ("met" if not ra_bad else "NOT met", "max Ra %.2f um" % max(f.ra_um for f in r.features) if not ra_bad else ", ".join(ra_bad))
    out["R-06"] = ("met" if r.stress_ratio <= 1 / 1.5 else "NOT met", f"sigma/Re {r.stress_ratio:.2f}")
    blind = [f.feature.name for f in r.features if f.budget_um and f.ron_um > 0.5 * f.budget_um and f.two_point_um < 0.2 * f.ron_um]
    out["R-07"] = ("met with a 3-point gauge" if blind else "met", ("two-point gauge blind on: " + ", ".join(blind)) if blind else "lobing small or visible")
    p = max(o.power_kW for o in r.ops)
    out["R-08"] = ("met" if p <= 15 else "NOT met", f"{p:.1f} kW")
    return out
