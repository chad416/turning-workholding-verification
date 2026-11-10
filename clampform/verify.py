"""Read a lathe program back and check the workholding physics block by block.

The verifier does not trust the planner: it parses the G-code text (FANUC or Sinumerik subset written by
gcode.py), keeps the modal state (tool, G96/G97, speed limit, spindle, clamp preset, dwell), simulates the
material as an outer and an inner radius per 0.05 mm of length, and for every cutting block recomputes the chip,
the cutting force (Kienzle), the spindle speed the control will actually run, the centrifugal loss and the grip.

Rules (a finding names the rule and the line):
  W1  grip at speed: mu (F_set - F_c(n)) / F_transfer >= S_z on every cutting block (VDI 3106 method)
  W2  spindle speed <= chuck rating and <= the program's speed limit; a speed limit is set before every G96
  W3  a clamp preset changes only with the spindle stopped, and a dwell follows before the spindle restarts
  W4  every groove plunge to depth is followed by a dwell of >= 2 revolutions (thin-wall spring-back)
  W5  the header's preset forces lie within the chuck's range
  W6  cutting power <= spindle power
  W7  finished features: roundness after release <= budget (needs the FE model), Ra <= requirement
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np

from . import clamp as clp
from . import cutting as ct
from .parts import Part, load_json
from .process import chuck_for, tools

DZ = 0.05


@dataclass
class Finding:
    rule: str
    line: int
    msg: str


@dataclass
class BlockCheck:
    line: int
    tool: str
    d: float
    ap: float
    n: float
    Fc: float
    grip: float
    F_cut: float
    finish_feature: str | None = None


@dataclass
class VerifyResult:
    findings: list[Finding] = field(default_factory=list)
    blocks: list[BlockCheck] = field(default_factory=list)
    feature_force: dict[str, float] = field(default_factory=dict)
    feature_ron_um: dict[str, float] = field(default_factory=dict)
    max_rpm: float = 0.0
    min_grip: float = math.inf

    @property
    def ok(self) -> bool:
        return not self.findings


_TOK = re.compile(r"([A-Z]+)\s*=?\s*(-?\d*\.?\d+)")


def _strip(line: str) -> str:
    line = re.sub(r"\(.*?\)", "", line)
    return line.split(";")[0].strip().upper()


def _header_forces(text: str) -> tuple[float | None, float | None]:
    m = re.search(r"CLAMP PRESET HIGH ([\d.]+) KN", text, re.I)
    lo = re.search(r"LOW ([\d.]+) KN", text, re.I)
    return (float(m.group(1)) * 1e3 if m else None, float(lo.group(1)) * 1e3 if lo else None)


def verify(text: str, p: Part, chuck_kind: str, fe=None) -> VerifyResult:
    T = tools()
    tool_by_no = {i + 1: k for i, k in enumerate(sorted(T))}
    lathe = load_json("machine.json")["lathe"]
    mc = lathe["clamp_mcodes"]
    fac = clp.factors()
    ch = chuck_for(p, chuck_kind)
    res = VerifyResult()
    F_high, F_low = _header_forces(text)
    if F_high is None:
        res.findings.append(Finding("W5", 0, "header gives no clamp preset force"))
        F_high = ch.F_max
    for name, F in (("high", F_high), ("low", F_low)):
        if F is not None and not (ch.F_min - 1 <= F <= ch.F_max + 1):
            res.findings.append(Finding("W5", 0, f"{name} preset {F/1e3:.1f} kN outside {ch.F_min/1e3:.1f}-{ch.F_max/1e3:.0f} kN"))
    # material model
    zmin = p.zmin(ch.grip_len)
    zs = np.arange(zmin, 2.0 + DZ, DZ)
    face0 = 1.0  # face allowance on the sawn bar or tube
    present = zs <= face0 + 1e-9
    r_out = np.where(present, (p.od if p.is_tube else p.stock_od) / 2, 0.0)
    r_in = np.where(present, (p.bore if p.is_tube else p.stock_id) / 2, 0.0)
    feats = {f.name: f for f in p.features}
    st = {"tool": None, "g": 0, "x": 220.0, "z": 100.0, "g96": False, "s": 0.0, "cap": None, "spin": False, "preset": "high",
          "dwell_since_switch": True, "pending_plunge": None, "line": 0}
    r_g = p.grip_r
    lines = text.splitlines()

    def speed(d: float) -> float:
        cap = min(st["cap"] or math.inf, ch.n_max, lathe["n_max_rpm"])
        n = ct.rpm(st["s"], d, cap) if st["g96"] else st["s"]
        return n

    for ln, raw in enumerate(lines, 1):
        s = _strip(raw)
        if not s or s.startswith("%") or s.startswith("O"):
            continue
        words = _TOK.findall(s)
        codes = [(a, float(b)) for a, b in words]
        gs = [int(v) for a, v in codes if a == "G"]
        ms = [f"M{int(v)}" for a, v in codes if a == "M"]
        vals = {a: v for a, v in codes if a not in ("G", "M")}
        if "LIMS" in vals:
            st["cap"] = vals["LIMS"]
        if 50 in gs and "S" in vals:
            st["cap"] = vals["S"]
            vals.pop("S")
        if 96 in gs:
            if st["cap"] is None:
                res.findings.append(Finding("W2", ln, "G96 without a spindle-speed limit (G50 / LIMS)"))
            st["g96"] = True
            st["s"] = vals.get("S", st["s"])
        if 97 in gs:
            st["g96"] = False
        if "T" in vals:
            tv = int(vals["T"])
            no = tv // 100 if tv >= 100 else tv
            st["tool"] = tool_by_no.get(no)
        for m in ms:
            if m in (mc["high"], mc["low"]):
                if st["spin"]:
                    res.findings.append(Finding("W3", ln, "clamp preset changed while the spindle turns"))
                st["preset"] = "high" if m == mc["high"] else "low"
                st["dwell_since_switch"] = False
            if m == "M3":
                if not st["dwell_since_switch"]:
                    res.findings.append(Finding("W3", ln, "spindle restarted without a dwell after the preset switch"))
                st["spin"] = True
            if m in ("M5", "M30"):
                st["spin"] = False
        if 4 in gs:
            st["dwell_since_switch"] = True
            if st["pending_plunge"] is not None:
                n = speed(st["pending_plunge"])
                t_dw = vals.get("X", vals.get("P", 0) / 1000 if "P" in vals else None)
                revs = vals["S"] if ("S" in vals and t_dw is None) else (t_dw or 0) * n / 60
                if revs < 2 - 1e-6:
                    res.findings.append(Finding("W4", ln, f"dwell at the groove bottom is {revs:.1f} rev (< 2)"))
                st["pending_plunge"] = None
            continue
        for g in gs:
            if g in (0, 1):
                st["g"] = g
        if "X" not in vals and "Z" not in vals:
            continue
        if st["pending_plunge"] is not None:
            res.findings.append(Finding("W4", ln, "groove plunge to depth not followed by a dwell"))
            st["pending_plunge"] = None
        x1, z1 = vals.get("X", st["x"]), vals.get("Z", st["z"])
        if st["g"] == 1 and st["tool"]:
            t = T[st["tool"]]
            kind = t["kind"]
            f = vals.get("F", st.get("f", 0.1))
            st["f"] = f
            r1 = x1 / 2
            za, zb = sorted((st["z"], z1))
            plunge = abs(z1 - st["z"]) < 1e-9 and abs(x1 - st["x"]) > 1e-9
            radial_turn = kind == "turn" and plunge
            if kind.startswith("groove"):  # the insert spans [z - width, z]
                sel = (zs >= za - t["width"] - 1e-9) & (zs <= zb + 1e-9) & present
            elif radial_turn:  # facing: the nose sweeps [r_min, r_max] at Z; material in front of it (z > Z) is cut
                rmin, rmax = sorted((st["x"] / 2, r1))
                sel = (zs > z1 + 1e-9) & present & (r_out > rmin + 1e-9) & (r_in < rmax - 1e-9)
            else:
                sel = (zs >= za - 1e-9) & (zs <= zb + 1e-9) & present
            ap, removed = 0.0, False
            outer = kind in ("turn", "groove_ext")
            if radial_turn:
                d_cut = x1
                if sel.any():
                    ap = float(zs[sel].max() - z1)
                    d_cut = 2 * float(min(r_out[sel].max(), rmax))
                    gone = sel & (r_in >= rmin - 1e-9)
                    present = present & ~gone
                    r_out = np.where(sel & ~gone, np.minimum(r_out, rmin), r_out)
                    removed = ap > 1e-6
            elif outer:
                if sel.any():
                    excess = r_out[sel] - r1
                    ap = float(max(excess.max(), 0.0))
                    if ap > 1e-6:
                        r_out[sel] = np.minimum(r_out[sel], r1)
                        removed = True
                d_cut = x1
            else:
                if sel.any():
                    excess = r1 - r_in[sel]
                    ap = float(max(excess.max(), 0.0))
                    if ap > 1e-6:
                        r_in[sel] = np.maximum(r_in[sel], r1)
                        removed = True
                d_cut = x1
            if removed:
                n = speed(max(d_cut, 1.0))
                res.max_rpm = max(res.max_rpm, n)
                if n > ch.n_max + 1 or (st["cap"] and n > st["cap"] + 1):
                    res.findings.append(Finding("W2", ln, f"spindle {n:.0f} rpm above the limit"))
                vc = math.pi * d_cut * n / 1000 if st["g96"] else math.pi * d_cut * st["s"] / 1000
                if plunge and kind.startswith("groove"):
                    cut = ct.plunge(t["width"], f, p.material, max(vc, 1.0), kind, t.get("gamma_deg", 0.0))
                    st["pending_plunge"] = d_cut
                else:
                    cut = ct.turning(min(ap, 50.0), f, t["rn"], t.get("kappa_deg", 90), p.material, max(vc, 1.0),
                                     "bore" if kind == "bore" else ("turn" if kind == "turn" else kind), t.get("gamma_deg", 6.0))
                F_set = F_high if st["preset"] == "high" else (F_low if F_low is not None else F_high)
                Fcent = ch.centrifugal(n, 2 * r_g)
                Ftr = cut.Fc * (d_cut / 2) / r_g
                grip = clp.grip_margin(F_set, Fcent, Ftr)
                res.min_grip = min(res.min_grip, grip)
                if grip < fac["S_z"] - 1e-6:
                    res.findings.append(Finding("W1", ln, f"grip {grip:.2f} < {fac['S_z']} at {n:.0f} rpm (F_set {F_set/1e3:.1f} kN, F_c {Fcent/1e3:.1f} kN)"))
                if ct.power_kW(cut.Fc, vc, lathe["efficiency"]) > lathe["P_spindle_kW"]:
                    res.findings.append(Finding("W6", ln, "cutting power above the spindle power"))
                fin = None
                for fname, ft in feats.items():
                    if abs(ft.r - r1) < 0.003 and (zb >= ft.z0 - 0.5 and za <= ft.z1 + 0.5) and not plunge:
                        fin = fname
                        side_ok = (ft.side == "od") == outer
                        if side_ok:
                            res.feature_force[fname] = max(F_set - Fcent, 0.0)
                            ra = ct.roughness(f, t["rn"])[0]
                            if ra > ft.ra_um + 1e-9:
                                res.findings.append(Finding("W7", ln, f"{fname}: Ra {ra:.2f} um > {ft.ra_um} um"))
                res.blocks.append(BlockCheck(ln, st["tool"], d_cut, ap, n, cut.Fc, grip, max(F_set - Fcent, 0.0), fin))
        st["x"], st["z"] = x1, z1
    if fe is not None:
        for fname, F in res.feature_force.items():
            f = feats[fname]
            stage = "A" if (fname == "OD" and _od_before_bore(res, p)) else "fin"
            _, m = fe.feature_profile(f, stage, ch.n_jaws, ch.half_angle, F)
            res.feature_ron_um[fname] = m.ron * 1e3
            if f.tol_um and m.ron * 1e3 > f.tol_um / 2:
                res.findings.append(Finding("W7", 0, f"{fname}: roundness after release {m.ron*1e3:.1f} um > budget {f.tol_um/2:.0f} um"))
    for fname in feats:
        if fname not in res.feature_force:
            res.findings.append(Finding("W7", 0, f"feature {fname} is never finished by the program"))
    return res


def _od_before_bore(res: VerifyResult, p: Part) -> bool:
    """True when the OD finish comes before the bore is opened up (the section is still the thick stock)."""
    od_line = next((b.line for b in res.blocks if b.finish_feature == "OD"), None)
    bore_line = next((b.line for b in res.blocks if b.tool in ("T03", "T04")), None)
    return od_line is not None and (bore_line is None or od_line < bore_line)
