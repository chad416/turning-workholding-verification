"""Analysis of alternatives for the workholding of one part (Wasson 2016, ch. 32, method of Fig. 32.7).

Candidates: chuck (3 jaws, 6 jaws, 3 pie jaws) x pressure scheme (single, two-stage). A candidate that misses a
must requirement (grip at speed, roundness budget, chuck force range) is not viable and is screened out before
scoring (Wasson's viable-alternative rule). Viable candidates are scored on 0-10 utility curves with fixed anchors
(not min-max over the candidates, which turns a 1 um difference into a 10-point swing): roundness margin earns full
marks at 50 % of the budget unused; cycle time scores 10 at the best candidate and 0 at twice that; grip margin scores
10 at 2 x S_z. Scores marked 'model' come from the evaluation, scores marked 'judgement' are written here with their
reason. Sensitivity: each
weight +-10 % (Wasson's definition) and 2000 random weight sets (uniform on the simplex).
"""

from __future__ import annotations

import numpy as np

from .process import StrategyResult

CRITERIA = {  # name: (weight, kind, reason)
    "roundness margin": (0.30, "model", "worst feature: 1 - RON / budget; full marks at 0.5"),
    "cycle time per part": (0.25, "model", "cutting + switching + set-up spread over a batch of 4 (make-to-order)"),
    "grip margin at speed": (0.10, "model", "lowest friction capacity / transferred force over all cuts"),
    "changeover for high-mix": (0.20, "judgement", "pie jaws are bored for each diameter; 6-jaw chucks need their own soft jaws"),
    "investment": (0.15, "judgement", "6-jaw compensating chuck ~2.5x a 3-jaw; a pie jaw set ~1.2x; two-stage needs a programmable pressure valve"),
}
JUDGEMENT = {  # (chuck kind, scheme) -> {criterion: score 0-10}
    ("3J", "single"): {"changeover for high-mix": 9, "investment": 10},
    ("3J", "two-stage"): {"changeover for high-mix": 9, "investment": 8},
    ("6J", "single"): {"changeover for high-mix": 6, "investment": 4},
    ("6J", "two-stage"): {"changeover for high-mix": 6, "investment": 3},
    ("PIE", "single"): {"changeover for high-mix": 3, "investment": 8},
    ("PIE", "two-stage"): {"changeover for high-mix": 3, "investment": 7},
}


def _kind(r: StrategyResult) -> str:
    return r.chuck.split("-")[0]


def viable(r: StrategyResult) -> tuple[bool, str]:
    if not r.feasible:
        return False, "; ".join(r.notes)
    if r.min_grip < 1.5 - 1e-6:
        return False, f"grip {r.min_grip:.2f} < 1.5"
    bad = [f.feature.name for f in r.features if not f.ok]
    if bad:
        return False, "roundness over budget: " + ", ".join(bad)
    return True, ""


def score(results: list[StrategyResult]) -> dict:
    cands = [r for r in results if viable(r)[0]]
    screened = {f"{r.chuck} {r.scheme}": viable(r)[1] for r in results if not viable(r)[0]}
    if not cands:
        return {"ranking": [], "screened": screened}
    names = [f"{r.chuck} {r.scheme}" for r in cands]
    t = np.array([r.cycle_s for r in cands])
    util = {
        "roundness margin": np.clip(np.array([1 - r.worst_ron_ratio for r in cands]) / 0.5, 0, 1) * 10,
        "cycle time per part": np.clip((2 * t.min() - t) / t.min(), 0, 1) * 10,
        "grip margin at speed": np.clip((np.array([r.min_grip for r in cands]) - 1.5) / 1.5, 0, 1) * 10,
    }
    S = np.zeros((len(cands), len(CRITERIA)))
    for j, (c, (w, kind, _)) in enumerate(CRITERIA.items()):
        if kind == "model":
            S[:, j] = util[c]
        else:
            S[:, j] = [JUDGEMENT[(_kind(r), r.scheme)][c] for r in cands]
    w = np.array([v[0] for v in CRITERIA.values()])
    tot = S @ w
    order = np.argsort(-tot)
    best = int(order[0])
    flips = []
    for j, c in enumerate(CRITERIA):
        for sgn in (-1, 1):
            w2 = w.copy()
            w2[j] *= 1 + 0.1 * sgn
            w2 /= w2.sum()
            if int(np.argmax(S @ w2)) != best:
                flips.append(f"{c} {'+' if sgn > 0 else '-'}10 %")
    rng = np.random.default_rng(7)
    W = rng.dirichlet(np.ones(len(w)), 2000)
    wins = np.bincount(np.argmax(S @ W.T, axis=0), minlength=len(cands)) / 2000
    return {
        "criteria": CRITERIA,
        "names": names,
        "scores": S,
        "total": tot,
        "ranking": [(names[i], float(tot[i]), float(wins[i])) for i in order],
        "flips": flips,
        "screened": screened,
    }
