"""FMEA of the workholding (Wasson eq. 34.41: RPN = S x O x D). Occurrence is read from the computed margin
with a fixed rule, so the ranking moves with the strategy; severity and detection are judgement per row."""

from __future__ import annotations

from .process import StrategyResult


def occurrence(margin: float) -> int:
    """Margin = capacity / demand (>1 good). Same rule shape as project 13's fmea.py."""
    for lim, o in ((0.8, 10), (1.0, 9), (1.2, 7), (1.5, 5), (2.0, 3), (3.0, 2)):
        if margin < lim:
            return o
    return 1


def rows(r: StrategyResult, part_is_tube: bool) -> list[dict]:
    worst = max(r.features, key=lambda f: (f.ron_um / f.budget_um) if f.budget_um else 0)
    ron_margin = worst.budget_um / max(worst.ron_um, 1e-9) if worst.budget_um else 10
    two_pt_blind = worst.two_point_um < 0.2 * max(worst.ron_um, 1e-9)
    grip_margin = r.min_grip / 1.5
    defl = max((f.tool_defl_um / (f.feature.tol_um / 4) if f.feature.tol_um else 0) for f in r.features)
    out = [
        {"mode": "part thrown at speed (centrifugal loss of grip)", "effect": "injury, machine damage", "S": 10,
         "margin": grip_margin, "D": 8, "detect": "none in the program; only the VDI calculation or a slip test"},
        {"mode": f"lobed fit not detected ({worst.feature.name})", "effect": "part binds or leaks at assembly",
         "S": 7, "margin": ron_margin, "D": 9 if two_pt_blind else 4,
         "detect": "two-point gauge blind to odd lobes" if two_pt_blind else "visible to the two-point gauge"},
        {"mode": "part slips under the cutting torque", "effect": "scrap, tool breakage", "S": 6, "margin": grip_margin, "D": 3,
         "detect": "witness marks / spindle load"},
        {"mode": "clamp yields the section (jaw marks, permanent set)", "effect": "scrap", "S": 5,
         "margin": 1 / max(r.stress_ratio * 1.5, 1e-9), "D": 3, "detect": "visual / roundness after release"},
        {"mode": "groove bottom off size (wall deflects under the tool)", "effect": "seal squeeze out of range", "S": 6,
         "margin": 1 / max(defl, 1e-9), "D": 6, "detect": "internal groove diameter is hard to gauge"},
    ]
    for row in out:
        row["O"] = occurrence(row["margin"])
        row["RPN"] = row["S"] * row["O"] * row["D"]
    return sorted(out, key=lambda x: -x["RPN"])
