"""Calculation reports (reports/*.md), lathe programs (reports/nc/) and figures (docs/img/)."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from . import plots
from .analysis import PartResult, run_part
from .audit07 import audit_all
from .clamp import chucks, factors
from .cutting import rpm
from .form import THETA, vblock_reading
from .harmfe import HarmonicModel, build_mesh, jaw_harmonics
from .parts import ROOT, load_parts
from .process import chuck_for
from .requirements import REQS
from .ring import ring_w

PARTS = ["TU-LD-80C", "TU-HD-160B", "GL-LD-80C", "GL-HD-160B", "PI-LD-80C", "PI-HD-160B"]


def _tbl(head: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def part_report(pr: PartResult) -> str:
    p = pr.part
    L = [f"# {p.pid}: {p.family}, {p.order}", ""]
    L.append(f"Material {p.material}. " + (f"Tube {p.od:g} x {(p.od - p.bore) / 2:g} mm; gland-seat counterbore D{p.counterbore['d']:g} {p.counterbore['fit']} x {p.counterbore['depth']:g} mm at the mouth (design variant)."
                                          if p.is_tube else f"Finished OD {p.od:g}, bore {p.bore:g}, length {p.length:g} mm from hollow bar {p.stock_od:g} x {p.stock_id:g}, gripped on the bar behind the part."))
    L.append(f"FE section mesh: {pr.fe.models['fin'].mesh.n_nodes} nodes (Q8, h = {pr.fe.h:.2f} mm), harmonics k = 0, 3, ..., {pr.fe.k_max}.")
    L += ["", "## Workholding strategies", ""]
    rows = []
    for r in pr.strategies:
        w = max((f for f in r.features if f.budget_um), key=lambda f: f.ron_um / f.budget_um, default=None)
        rows.append([r.chuck, r.scheme, f"{r.F_high/1e3:.1f}", f"{r.F_low/1e3:.1f}", f"{r.g50_high:.0f} / {r.g50_low:.0f}", f"{r.min_grip:.2f}",
                     f"{w.feature.name}: {w.ron_um:.1f} / {w.budget_um:.0f}" if w else "-", f"{w.two_point_um:.1f}" if w else "-",
                     f"{r.stress_ratio:.2f}", f"{r.cycle_s/60:.2f}", "; ".join(r.notes) or ""])
    L.append(_tbl(["chuck", "pressure", "F high kN", "F low kN", "G50 rough / finish", "min grip (>= 1.5)", "worst RONt / budget um",
                   "two-point sees um", "clamp sigma/Re", "min per part (batch 4)", "notes"], rows))
    L += ["", f"Chosen by the trade study: **{pr.chosen.chuck} {pr.chosen.scheme}**. Baseline (one pressure, 3 jaws): {pr.baseline.chuck} single.", ""]
    L += ["## Features: baseline and chosen", ""]
    for lab, r in (("baseline", pr.baseline), ("chosen", pr.chosen)):
        rows = [[f.feature.name, f.feature.fit or "-", f"{f.feature.d:g}", f"{f.F_cut/1e3:.1f}", f"{f.ron_um:.1f}", f"{f.budget_um:.0f}" if f.budget_um else "-",
                 f"{f.two_point_um:.1f}", f"{f.v108_um:.1f}", f"{f.tool_defl_um:.1f}", f"{f.ra_um:.2f} / {f.feature.ra_um}", "ok" if f.ok else "**over**"]
                for f in r.features]
        L += [f"**{lab}: {r.chuck} {r.scheme}**", "",
              _tbl(["feature", "fit", "D mm", "force during finish kN", "RONt um", "budget um", "two-point um", "108 deg V um", "tool-load size error um",
                    "Ra um / req", "R-04"], rows), ""]
    L += ["## Requirements", ""]
    L.append(_tbl(["ID", "requirement", "source", "method", "baseline", "chosen"],
                  [[i, t, s, m, f"{pr.req_base[i][0]} ({pr.req_base[i][1]})" if i in pr.req_base else "-",
                    f"{pr.req_chosen[i][0]} ({pr.req_chosen[i][1]})" if i in pr.req_chosen else "-"] for i, t, s, m in REQS]))
    L += ["", "## Trade study", ""]
    sc = pr.aoa
    if sc["ranking"]:
        L.append(_tbl(["candidate", "score", "wins of 2000 random weight sets"], [[n, f"{t:.2f}", f"{w*100:.0f} %"] for n, t, w in sc["ranking"]]))
        L.append("")
        L.append("Weight changes of +-10 % that flip the winner: " + (", ".join(sc["flips"]) or "none") + ".")
    for k, v in sc["screened"].items():
        L.append(f"- screened out: {k}: {v}")
    L += ["", "## FMEA (RPN = S x O x D; O from the computed margin)", ""]
    for lab, rows_ in (("baseline", pr.fmea_base), ("chosen", pr.fmea_chosen)):
        L += [f"**{lab}**", "", _tbl(["failure mode", "effect", "margin", "S", "O", "D", "RPN", "detection"],
                                     [[x["mode"], x["effect"], f"{x['margin']:.2f}", x["S"], x["O"], x["D"], x["RPN"], x["detect"]] for x in rows_]), ""]
    if pr.sens:
        L += ["## Sensitivity (3 jaws, two-stage: worst RONt / budget)", "",
              _tbl(["input", "low", "high"], [[a, f"{b:.2f}", f"{c:.2f}"] for a, b, c in pr.sens]),
              f"\nBase value {pr.sens_base:.2f}.", ""]
    if pr.verified:
        L += ["## Program read-back (verify.py)", ""]
        for d, v in pr.verified.items():
            L.append(f"- {d}: {'PASS' if v.ok else 'FINDINGS'}; {len(v.blocks)} cutting blocks, max {v.max_rpm:.0f} rpm, min grip {v.min_grip:.2f}; "
                     + ", ".join(f"{k} {x:.1f} um" for k, x in v.feature_ron_um.items()))
            for f in v.findings[:8]:
                L.append(f"  - {f.rule} line {f.line}: {f.msg}")
    return "\n".join(L) + "\n"


def audit_section() -> tuple[str, list]:
    A = audit_all()
    rows = [[a.program, f"{a.stock_d:g}", a.chuck, f"{a.g50:.0f}", "yes" if a.faces_to_centre else "no", a.governing_cut, f"{a.F_set/1e3:.1f}",
             f"{a.F_cent_at_g50/1e3:.1f}", f"{a.F_residual/1e3:.1f}", f"{a.n_allow_face:.0f}", f"{a.jaw_mr_ratio:.2f}"] for a in A]
    txt = _tbl(["07 program", "bar D", "chuck", "G50", "faces to X0 under G96", "heaviest cut", "static force needed kN",
                "jaw centrifugal force at G50 kN", "force left at G50 kN", "allowed speed rpm", "soft-jaw m r / rated"], rows)
    return txt, A


def figures(results: dict[str, PartResult], img: Path) -> None:
    # 1) FE check against thin-ring theory
    R, t, b = 50.0, 2.0, 10.0
    M = HarmonicModel(build_mesh([(R - t / 2, R + t / 2, 0, b)], 0.5), 210e3, 0.0)
    th = np.linspace(0, 2 * np.pi / 3, 41)
    ur = np.zeros_like(th)
    nn = M.nodes_on(R, 0, b)
    for k, c in jaw_harmonics(3, 0.02, 90):
        u = M.solve(k, M.surface_load(k, R + t / 2, 0, b, -c / ((R + t / 2) * b)))
        ur += u[nn, 0].mean() * np.cos(k * th)
    plots.fe_check(th, -ur * 1e4, ring_w(th, 3, 1e4, R, 210e3, b, t, 0.02), img / "fe_check_ring.png",
                   "Model check: ring R50 x 2 x 10 mm, 3 jaws x 10 kN: harmonic FE vs closed form")
    # 2) gauges
    plots.gauge_sensitivity(img / "gauge_sensitivity.png")
    # 3) jaw reach
    curves = []
    for pid, col in (("TU-LD-80C", "b"), ("TU-HD-160B", "a"), ("GL-LD-80C", "c")):
        if pid in results and results[pid].decay is not None:
            x, y = results[pid].decay
            curves.append((f"{pid} bore", x, y, col))
    plots.decay(curves, img / "jaw_reach.png")
    # 4) speed limit
    A = audit_all()
    rows = []
    for a, col in ((next(x for x in A if x.stock_d > 120), "b"), (next(x for x in A if x.stock_d < 120), "a")):
        ch = chucks()[a.chuck]
        rows.append({"label": f"{a.chuck}, bar D{a.stock_d:g}, set {a.F_set/1e3:.0f} kN (soft jaws)", "F_set": a.F_set, "n_max": 4000,
                     "cent": (lambda n, ch=ch, d=a.stock_d: ch.centrifugal(n, d)), "g50_derived": math.floor(a.n_allow_face / 50) * 50, "col": col})
    plots.grip_vs_speed(rows, img / "speed_limit.png")
    # 5) per part
    for pid, pr in results.items():
        labs = [f"{r.chuck} {r.scheme}" for r in pr.strategies]
        worst = [max((f.ron_um / f.budget_um for f in r.features if f.budget_um), default=0) for r in pr.strategies]
        plots.bars(f"{pid}: worst roundness after release / budget", labs, worst, 1.0, img / f"{pid}_strategies.png", "RONt / budget")
        plots.aoa_bars(pid, pr.aoa, img / f"{pid}_aoa.png")
    # 6) LD tube: profiles, window, sensitivity
    pr = results.get("TU-LD-80C")
    if pr:
        f = pr.part.features[0]
        profs = []
        for r, col in ((pr.strategies[0], "b"), (pr.strategies[1], "d"), (pr.strategies[2], "c")):
            fr = next(x for x in r.features if x.feature.name == f.name)
            ch = chuck_for(pr.part, r.chuck.split("-")[0])
            dev, _ = pr.fe.feature_profile(f, "fin", ch.n_jaws, ch.half_angle, fr.F_cut)
            profs.append((f"{r.chuck} {r.scheme}: RONt {fr.ron_um:.0f} um, two-point {fr.two_point_um:.1f} um, 108 deg V {vblock_reading(dev, 108)*1e3:.0f} um", dev, col))
        plots.polar_profiles(f"TU-LD-80C counterbore D84 H8 after release", profs, f.tol_um / 2, img / "TU-LD-80C_profiles.png", 400)
        ch = chuck_for(pr.part, "3J")
        fin = next(o for o in pr.strategies[1].ops if o.op.finish)
        Fs = np.linspace(2e3, 30e3, 120)
        ns = np.linspace(200, 3000, 120)
        FF, NN = np.meshgrid(Fs, ns, indexing="ij")
        cent = ch.centrifugal(NN, 2 * pr.part.grip_r)
        fac = factors()
        grip_ok = FF >= fac["S_sp"] * (fac["S_z"] * fin.F_transfer / fac["mu"] + cent)
        unit = pr.fe.feature_profile(f, "fin", 3, ch.half_angle, 1e3)[1].ron * 1e3 / 1e3
        ron = np.maximum(FF - cent, 0) * unit
        n_fin = rpm(fin.op.vc, fin.op.d, 1e9)
        plots.window("TU-LD-80C finishing the counterbore in 3 jaws", Fs, ns, grip_ok, ron, f.tol_um / 2, ch.F_min,
                     img / "TU-LD-80C_window.png",
                     [(n_fin, pr.strategies[0].F_high, "one pressure (set by roughing)"), (n_fin, pr.strategies[1].F_low, "two-stage (chuck minimum)")])
        if pr.sens:
            plots.tornado("TU-LD-80C, 3 jaws two-stage: what moves the roundness verdict", pr.sens, pr.sens_base, img / "TU-LD-80C_sensitivity.png",
                          "worst RONt / budget (1 = limit)")


def run(out: Path | None = None, figs: bool = True, parts: list[str] | None = None, fast: bool = False) -> dict[str, PartResult]:
    out = out or ROOT / "reports"
    (out / "nc").mkdir(parents=True, exist_ok=True)
    results = {}
    for pid in parts or PARTS:
        pr = run_part(pid, with_programs=True, with_sens=not fast)
        results[pid] = pr
        (out / f"{pid}.md").write_text(part_report(pr), encoding="utf-8")
        (out / "nc" / f"{pid}.nc").write_text(pr.programs["fanuc"], encoding="utf-8", newline="\n")
        (out / "nc" / f"{pid}.mpf").write_text(pr.programs["sinumerik"], encoding="utf-8", newline="\n")
        print(f"{pid}: chosen {pr.chosen.chuck} {pr.chosen.scheme}; programs {'PASS' if all(v.ok for v in pr.verified.values()) else 'FINDINGS'}", flush=True)
        pr.fe.models = {k: v for k, v in pr.fe.models.items()}  # keep for figures
    audit_txt, _ = audit_section()
    S = ["# Summary", "", "## Project 07 programs: speed limit audit", "", audit_txt, "", "## Chosen workholding per part", ""]
    S.append(_tbl(["part", "baseline worst RONt / budget", "chosen", "chosen worst RONt / budget", "G50 rough / finish", "programs"],
                  [[pid, f"{pr.baseline.worst_ron_ratio:.2f}", f"{pr.chosen.chuck} {pr.chosen.scheme}", f"{pr.chosen.worst_ron_ratio:.2f}",
                    f"{pr.chosen.g50_high:.0f} / {pr.chosen.g50_low:.0f}", "PASS" if all(v.ok for v in pr.verified.values()) else "FINDINGS"]
                   for pid, pr in results.items()]))
    (out / "SUMMARY.md").write_text("\n".join(S) + "\n", encoding="utf-8")
    if figs:
        figures(results, ROOT / "docs" / "img")
    return results
