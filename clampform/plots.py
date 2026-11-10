"""Figures of running outputs (docs/img)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .form import THETA, vblock_reading  # noqa: E402

C = {"a": "#2a6f97", "b": "#c8553d", "c": "#588157", "d": "#8d6a9f", "g": "#6c757d", "k": "#222222"}


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def polar_profiles(title: str, profiles: list[tuple[str, np.ndarray, str]], budget_um: float, path: Path, mag: float) -> None:
    """Released profiles (deviation in um) drawn on a magnified polar plot."""
    fig = plt.figure(figsize=(6.4, 5.6))
    ax = fig.add_subplot(111, projection="polar")
    base = 1.0
    th = np.append(THETA, THETA[0])
    ax.plot(th, np.full_like(th, base), color=C["g"], lw=0.8, ls=":", label="nominal circle")
    for lab, dev, col in profiles:
        d = np.append(dev, dev[0]) * 1e3
        ax.plot(th, base + d / mag, color=C[col], lw=1.8, label=lab)
    for j in range(3):
        ax.annotate("jaw", xy=(2 * math.pi * j / 3, base + 0.05), color=C["k"], fontsize=8, ha="center")
    ax.set_rticks([])
    ax.set_title(f"{title}\n(deviation magnified: {mag:g} um per unit radius; budget {budget_um:.0f} um)", fontsize=10)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.15, -0.18), fontsize=8, frameon=False)
    _save(fig, path)


def decay(curves: list[tuple[str, np.ndarray, np.ndarray, str]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for lab, x, y, col in curves:
        ax.plot(x, y, color=C[col], lw=2, label=lab)
    ax.axvline(0, color=C["g"], lw=0.8, ls=":")
    ax.text(0.5, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 1, "jaw edge", fontsize=8, color=C["g"])
    ax.set_xlabel("distance from the jaw edge, away from the jaws (mm)")
    ax.set_ylabel("roundness after release per 10 kN (um)")
    ax.set_title("How far the jaws reach: lobing of the bore along the part (3 jaws)")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.3)
    _save(fig, path)


def grip_vs_speed(rows: list[dict], path: Path) -> None:
    """Remaining clamping force vs spindle speed for set forces, with the program's G50 and the derived limit."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for r in rows:
        n = np.linspace(0, r["n_max"], 200)
        ax.plot(n, (r["F_set"] - r["cent"](n)) / 1e3, color=C[r["col"]], lw=2, label=r["label"])
        ax.axvline(r["g50_derived"], color=C[r["col"]], lw=1, ls="--")
        ax.text(r["g50_derived"], ax.get_ylim()[0] if False else 2, f"  derived limit {r['g50_derived']:.0f}", rotation=90, fontsize=7,
                color=C[r["col"]], va="bottom")
    ax.axvline(3500, color=C["k"], lw=1.2, ls=":")
    ax.text(3500, 5, " G50 S3500\n (generic header)", fontsize=8)
    ax.axhline(0, color=C["k"], lw=0.8)
    ax.set_xlabel("spindle speed (rpm)")
    ax.set_ylabel("force still on the part (kN)")
    ax.set_title("Centrifugal loss of grip: set force minus jaw centrifugal force")
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    ax.grid(alpha=0.3)
    _save(fig, path)


def gauge_sensitivity(path: Path) -> None:
    angles = np.linspace(50, 150, 101)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for k, col in ((3, "b"), (5, "a"), (6, "c")):
        dev = np.cos(k * THETA)
        ax.plot(angles, [vblock_reading(dev, a) / 2 for a in angles], color=C[col], lw=2, label=f"{k} lobes")
        half = len(dev) // 2
        tp = (dev[:half] + dev[half:])
        ax.scatter([50], [(tp.max() - tp.min()) / 2], color=C[col], marker="<", s=40)
    ax.set_xlabel("V-block included angle (deg)")
    ax.set_ylabel("reading / true roundness")
    ax.set_title("What a gauge sees of a lobed part (markers at left: two-point gauge)")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.3)
    _save(fig, path)


def window(title: str, Fs: np.ndarray, ns: np.ndarray, grip_ok: np.ndarray, ron: np.ndarray, budget: float, Fmin: float, path: Path,
           mark: list[tuple[float, float, str]]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ok = grip_ok & (ron <= budget)
    ax.contourf(ns, Fs / 1e3, ok.astype(float), levels=[-0.5, 0.5, 1.5], colors=["#f2dcd7", "#d8ead3"], alpha=0.9)
    cs = ax.contour(ns, Fs / 1e3, ron, levels=[budget * 0.5, budget, budget * 2], colors=[C["c"], C["b"], C["b"]], linewidths=[1, 2, 1])
    ax.clabel(cs, fmt=lambda v: f"RON {v:.0f} um", fontsize=7)
    ax.contour(ns, Fs / 1e3, grip_ok.astype(float), levels=[0.5], colors=[C["k"]], linewidths=2)
    ax.axhline(Fmin / 1e3, color=C["g"], ls=":", lw=1)
    ax.text(ns[0], Fmin / 1e3, " chuck minimum", fontsize=7, va="bottom", color=C["g"])
    for n, F, lab in mark:
        ax.plot(n, F / 1e3, "o", color=C["k"])
        ax.annotate(lab, (n, F / 1e3), textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax.set_xlabel("spindle speed during the finishing cut (rpm)")
    ax.set_ylabel("static clamping force set (kN)")
    ax.set_title(title + "\ngreen: grip >= S_z and roundness within budget; black line: grip limit")
    _save(fig, path)


def bars(title: str, labels: list[str], vals: list[float], budget: float, path: Path, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    cols = [C["c"] if v <= budget else C["b"] for v in vals]
    ax.bar(range(len(vals)), vals, color=cols)
    ax.axhline(budget, color=C["k"], ls="--", lw=1)
    ax.text(len(vals) - 0.5, budget, " budget", va="bottom", ha="right", fontsize=8)
    ax.set_xticks(range(len(vals)), labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    _save(fig, path)


def tornado(title: str, rows: list[tuple[str, float, float]], base: float, path: Path, xlabel: str) -> None:
    rows = sorted(rows, key=lambda r: abs(r[2] - r[1]))
    fig, ax = plt.subplots(figsize=(7.2, 0.5 * len(rows) + 1.4))
    for i, (lab, lo, hi) in enumerate(rows):
        ax.barh(i, hi - base, left=base, color=C["b"])
        ax.barh(i, lo - base, left=base, color=C["a"])
    ax.axvline(base, color=C["k"], lw=1)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    _save(fig, path)


def fe_check(theta: np.ndarray, fe: np.ndarray, ring: np.ndarray, path: Path, label: str) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(np.degrees(theta), ring * 1e3, color=C["k"], lw=2, label="thin-ring theory (Fourier series)")
    ax.plot(np.degrees(theta), fe * 1e3, "o", ms=3, color=C["b"], label="harmonic FE, Q8")
    ax.set_xlabel("angle from a jaw (deg)")
    ax.set_ylabel("radial displacement (um)")
    ax.set_title(label)
    ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.3)
    _save(fig, path)


def aoa_bars(part: str, sc: dict, path: Path) -> None:
    if not sc["ranking"]:
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    names = [r[0] for r in sc["ranking"]]
    tot = [r[1] for r in sc["ranking"]]
    wins = [r[2] * 100 for r in sc["ranking"]]
    ax.barh(range(len(names))[::-1], tot, color=C["a"])
    for i, (t, w) in enumerate(zip(tot, wins)):
        ax.text(t, len(names) - 1 - i, f"  {t:.1f}  (wins {w:.0f} % of random weights)", va="center", fontsize=8)
    ax.set_yticks(range(len(names))[::-1], names, fontsize=8)
    ax.set_xlim(0, 13)
    ax.set_xlabel("weighted score (0-10)")
    scr = "; ".join(f"{k}: {v}" for k, v in sc["screened"].items())
    ax.set_title(f"{part}: trade study of the viable workholding options", fontsize=10)
    if scr:
        fig.text(0.01, -0.08, "screened out: " + scr[:260], fontsize=7, wrap=True)
    _save(fig, path)
