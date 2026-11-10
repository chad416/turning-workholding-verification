"""Operation plan per part, and the workholding evaluation of a plan under a clamping strategy.

A strategy is a chuck (3 jaws, 6 jaws, or 3 pie jaws) and a pressure scheme:
  single     one static clamping force for the whole program, set by the most demanding operation (the usual way);
  two-stage  roughing at the high force, then spindle stop, switch to the low preset, dwell, and finish at the
             lowest force the finishing cuts need (VDI method), but not below the chuck's minimum.
For every operation the spindle speed follows G96 (constant surface speed) up to the program's G50 limit, the
centrifugal loss follows the speed, and the force that squeezes the part during a finishing cut is F_sp0 - F_c(n).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import clamp as clp
from . import cutting as ct
from .form import PartFE
from .parts import Feature, Part, load_json

TOOLS = None


def tools() -> dict:
    global TOOLS
    if TOOLS is None:
        TOOLS = load_json("tools.json")["tools"]
    return TOOLS


@dataclass
class Op:
    name: str
    tool: str
    kind: str  # turn, bore, groove_ext, groove_int, face
    d: float  # diameter being cut (mm): the finished diameter of this pass
    ap: float  # radial depth (turning) or insert width (plunge)
    f: float
    vc: float
    z0: float
    z1: float
    finish: bool = False
    feature: str | None = None
    stage: str = "fin"  # section geometry when the cut is made
    plunge: bool = False
    d_min_speed: float = 0.0  # smallest diameter reached (for the speed of a facing cut)
    entry_plunge: bool = False  # a groove finish starts with a full-width plunge through the bottom allowance

    @property
    def length(self) -> float:
        return abs(self.z1 - self.z0) if not self.plunge else self.ap

    def cut(self, material: str, **kw) -> ct.Cut:
        t = tools()[self.tool]
        if self.plunge:
            return ct.plunge(t["width"], self.f, material, self.vc, self.kind, t.get("gamma_deg", 0.0), **kw)
        kind = "bore" if self.kind == "bore" else ("turn" if self.kind in ("turn", "face") else self.kind)
        side = ct.turning(self.ap, self.f, t["rn"], t.get("kappa_deg", 90), material, self.vc, kind, t.get("gamma_deg", 6.0), **kw)
        if self.entry_plunge:  # the heavier of the entry plunge and the side pass governs the clamping force
            entry = ct.plunge(t["width"], t["f"], material, self.vc, self.kind, t.get("gamma_deg", 0.0), **kw)
            return entry if entry.Fc > side.Fc else side
        return side


def _passes(d_from: float, d_to: float, ap_max: float) -> list[tuple[float, float]]:
    """Radial passes from d_from to d_to (either direction): list of (diameter after the pass, ap)."""
    total = abs(d_from - d_to) / 2
    if total <= 1e-9:
        return []
    n = max(1, math.ceil(total / ap_max - 1e-9))
    ap = total / n
    s = 1 if d_to > d_from else -1
    return [(d_from + s * 2 * ap * (i + 1), ap) for i in range(n)]


RA_MARGIN = 0.8  # finishing feeds are chosen for 80 % of the Ra requirement


def _ffin(tool: str, ra_req: float, key: str = "f") -> float:
    t = tools()[tool]
    return ct.feed_for_ra(RA_MARGIN * ra_req, t["rn"], t[key])


def plan(p: Part, sequence: str = "usual") -> list[Op]:
    """Operations in program order. sequence 'usual' finishes each surface right after roughing it (as a
    part-family generator does); 'rough_first' does all roughing first, then all finishing (needed for two-stage)."""
    T = tools()
    rough, fin = [], []
    L = p.length
    if p.is_tube:
        cb = p.counterbore
        rough.append(Op("face tube end", "T01", "face", p.od, 1.0, 0.2, T["T01"]["vc"], 0, 0, d_min_speed=p.bore))
        for d, ap in _passes(p.bore, cb["d"] - 2 * T["T04"]["ap"], T["T03"]["ap"]):
            rough.append(Op("rough counterbore", "T03", "bore", d, ap, T["T03"]["f"], T["T03"]["vc"], -cb["depth"], 0))
        fin.append(Op("finish counterbore", "T04", "bore", cb["d"], T["T04"]["ap"], _ffin("T04", cb["ra_um"]), T["T04"]["vc"], -cb["depth"], 0,
                      True, "gland-seat counterbore"))
        return rough + fin
    zend = -L - p.over_end
    rough.append(Op("face", "T01", "face", p.stock_od, 1.0, T["T01"]["f"], T["T01"]["vc"], 0, 0, d_min_speed=p.stock_id))
    for d, ap in _passes(p.stock_od, p.od + 2 * T["T02"]["ap"], T["T01"]["ap"]):
        rough.append(Op("rough OD", "T01", "turn", d, ap, T["T01"]["f"], T["T01"]["vc"], zend, 0, stage="A"))
    od_fin = Op("finish OD", "T02", "turn", p.od, T["T02"]["ap"], _ffin("T02", p.od_ra), T["T02"]["vc"], zend, 0, True, "OD", "A")
    id_rough = [Op("rough bore", "T03", "bore", d, ap, T["T03"]["f"], T["T03"]["vc"], zend, 0)
                for d, ap in _passes(p.stock_id, p.bore - 2 * T["T04"]["ap"], T["T03"]["ap"])]
    id_fin = Op("finish bore", "T04", "bore", p.bore, T["T04"]["ap"], _ffin("T04", p.bore_ra), T["T04"]["vc"], zend, 0, True, "bore")
    g_rough, g_fin = [], []
    for g in p.grooves:
        tl = "T06" if g["side"] == "id" else "T05"
        kind = "groove_int" if g["side"] == "id" else "groove_ext"
        start = p.bore if g["side"] == "id" else p.od
        leave = 0.2
        depth = abs(g["bottom_d"] - start) / 2 - leave
        nplunge = max(1, math.ceil((g["width"] - 1e-9) / T[tl]["width"]))
        za, zb = -g["z"] - g["width"], -g["z"]
        for i in range(nplunge):
            zc = zb - i * (g["width"] - T[tl]["width"]) / max(nplunge - 1, 1) if nplunge > 1 else zb
            g_rough.append(Op(f"rough {g['name']}", tl, kind, start + (1 if g["side"] == "id" else -1) * 2 * depth, depth,
                              T[tl]["f"], T[tl]["vc"], zc - T[tl]["width"], zc, plunge=True))
        g_fin.append(Op(f"finish {g['name']}", tl, kind, g["bottom_d"], leave, _ffin(tl, g["ra_um"], "f_side"), T[tl]["vc"], za, zb, True, g["name"],
                        entry_plunge=True))
    if sequence == "usual":
        return rough + [od_fin] + id_rough + [id_fin] + g_rough + g_fin
    for o in id_rough:
        o.stage = "fin"
    od_fin.stage = "fin"
    return rough + id_rough + g_rough + [od_fin, id_fin] + g_fin


# --- evaluation -------------------------------------------------------------------------------------------------
@dataclass
class OpResult:
    op: Op
    n: float
    Fc: float
    F_transfer: float
    F_req0: float  # static force this op needs at its speed (VDI form)
    F_set: float = 0.0
    F_cent: float = 0.0
    F_cut: float = 0.0
    grip: float = 0.0  # friction capacity / transferred force at speed (requirement >= S_z)
    power_kW: float = 0.0
    time_s: float = 0.0
    ra_um: float = 0.0


@dataclass
class FeatureResult:
    feature: Feature
    F_cut: float
    ron_um: float
    two_point_um: float
    v108_um: float
    budget_um: float
    tool_defl_um: float
    ra_um: float

    @property
    def ok(self) -> bool:
        return self.budget_um <= 0 or self.ron_um <= self.budget_um


@dataclass
class StrategyResult:
    part: str
    chuck: str
    scheme: str
    F_high: float
    F_low: float
    g50_high: float
    g50_low: float
    feasible: bool
    ops: list[OpResult] = field(default_factory=list)
    features: list[FeatureResult] = field(default_factory=list)
    cycle_s: float = 0.0
    setup_min: float = 0.0
    min_grip: float = 0.0
    stress_ratio: float = 0.0  # clamp von Mises at F_high / Re
    notes: list[str] = field(default_factory=list)

    @property
    def worst_ron_ratio(self) -> float:
        r = [f.ron_um / f.budget_um for f in self.features if f.budget_um > 0]
        return max(r) if r else 0.0


def chuck_for(p: Part, kind: str) -> clp.Chuck:
    big = p.grip_r * 2 > 120
    return clp.chucks()[f"{kind}-{'315' if big else '210'}"]


def _speed(op: Op, g50: float, ch: clp.Chuck, n_lathe: float) -> float:
    d = op.d_min_speed or op.d
    return ct.rpm(op.vc, d, min(g50, ch.n_max, n_lathe))


def evaluate(p: Part, fe: PartFE, chuck_kind: str, scheme: str, batch: int = 4, sens: dict | None = None,
             g50: float | None = None) -> StrategyResult:
    """Evaluate one workholding strategy. sens: overrides for the sensitivity study (mu, kc_scale, thrust_ratio,
    K_wear, mass_scale). g50: force a program G50 (e.g. 3500, as written by a generic header) instead of deriving it."""
    sens = sens or {}
    ch = chuck_for(p, chuck_kind)
    if "mass_scale" in sens:
        ch.m_top *= sens["mass_scale"]
    if "fmin_frac" in sens:
        ch.F_min = sens["fmin_frac"] * ch.F_max
    fac = clp.factors()
    mu = sens.get("mu", fac["mu"])
    S_z, S_sp = fac["S_z"], fac["S_sp"]
    lathe = load_json("machine.json")["lathe"]
    seq = "rough_first" if scheme == "two-stage" else "usual"
    ops = plan(p, seq)
    kw = {k: sens[k] for k in ("kc_scale", "thrust_ratio", "K_wear") if k in sens}
    r_g = p.grip_r
    grip_d = 2 * r_g
    # 1) what each op needs at the speed it would run without any extra limit
    res: list[OpResult] = []
    for o in ops:
        c = o.cut(p.material, **kw)
        Ft = c.Fc * (o.d / 2) / r_g
        n0 = math.ceil(_speed(o, lathe["n_max_rpm"], ch, lathe["n_max_rpm"]) / 50) * 50  # G50 is set in 50 rpm steps
        res.append(OpResult(o, n0, c.Fc, Ft, clp.required_static(Ft, ch.centrifugal(n0, grip_d), mu, S_z, S_sp)))
    rough = [r for r in res if not (scheme == "two-stage" and r.op.finish)]
    fin = [r for r in res if scheme == "two-stage" and r.op.finish]
    F_high = max(r.F_req0 for r in rough)
    F_low = max((r.F_req0 for r in fin), default=0.0)
    notes = []
    feasible = True
    if F_high > ch.F_max:
        notes.append(f"needed static force {F_high/1e3:.1f} kN exceeds the chuck's {ch.F_max/1e3:.0f} kN")
        feasible = False
        F_high = ch.F_max
    if scheme == "two-stage":
        if F_low < ch.F_min:
            notes.append(f"low stage raised to the chuck minimum {ch.F_min/1e3:.1f} kN (cut needs {F_low/1e3:.1f} kN)")
            F_low = ch.F_min
    # 2) G50 per stage: the lowest speed limit over the ops of that stage (VDI: grip must hold at speed)
    def g50_for(rs: list[OpResult], F: float) -> float:
        lim = min(clp.speed_limit(ch, F, r.F_transfer, grip_d, mu, S_z, S_sp) for r in rs)
        return math.floor(min(lim, ch.n_max, lathe["n_max_rpm"]) / 50) * 50
    gh = g50 if g50 is not None else g50_for(rough, F_high)
    gl = (g50 if g50 is not None else g50_for(fin, F_low)) if fin else gh
    # 3) run every op at its stage's force and G50
    t_total = 0.0
    for r in res:
        stage_low = scheme == "two-stage" and r.op.finish
        F = F_low if stage_low else F_high
        cap = gl if stage_low else gh
        n = _speed(r.op, cap, ch, lathe["n_max_rpm"])
        r.n = n
        r.F_set = F
        r.F_cent = ch.centrifugal(n, grip_d)
        r.F_cut = max(F - r.F_cent, 0.0)
        r.grip = clp.grip_margin(F, r.F_cent, r.F_transfer, mu)
        r.power_kW = ct.power_kW(r.Fc, r.op.vc, lathe["efficiency"])
        n_at_d = ct.rpm(r.op.vc, r.op.d, min(cap, ch.n_max, lathe["n_max_rpm"]))
        if r.op.kind == "face":
            # facing from the OD to d_min at constant vc: integrate dt = dr / (f n(r))
            ds = [r.op.d - i * (r.op.d - r.op.d_min_speed) / 40 for i in range(41)]
            t = sum(abs(ds[i] - ds[i + 1]) / 2 / (r.op.f * ct.rpm(r.op.vc, 0.5 * (ds[i] + ds[i + 1]), min(cap, ch.n_max)) / 60) for i in range(40))
        else:
            t = r.op.length / (r.op.f * n_at_d / 60)
        r.time_s = t
        t_total += t + 2.0  # approach / retract per pass
        t_ra = tools()[r.op.tool]
        r.ra_um = ct.roughness(r.op.f, t_ra["rn"])[0]
    tools_used = len({r.op.tool for r in res})
    t_total += tools_used * lathe["tool_change_s"] * 2
    if scheme == "two-stage":
        t_total += lathe["clamp_switch_s"] + 4.0  # spindle stop, switch, dwell, run-up
    min_grip = min(r.grip for r in res)
    if min_grip < S_z - 1e-6:
        notes.append(f"grip at speed {min_grip:.2f} < S_z = {S_z}")
    # 4) features
    feats = []
    nj = ch.n_jaws
    for f in p.features:
        fr = [r for r in res if r.op.finish and r.op.feature == f.name]
        if not fr:
            continue
        r = fr[0]
        prof, m = fe.feature_profile(f, r.op.stage, nj, ch.half_angle, r.F_cut)
        from .form import two_point_reading, vblock_reading
        budget = f.tol_um / 2 if f.tol_um else 0.0
        c = r.op.cut(p.material, **kw)
        Frad = c.Fp if not r.op.plunge else c.Ff
        defl = fe.tool_compliance(f, r.op.stage) * Frad * 1e3 if sens.get("tool_defl", True) else 0.0
        feats.append(FeatureResult(f, r.F_cut, m.ron * 1e3, two_point_reading(prof) * 1e3, vblock_reading(prof, 108) * 1e3, budget,
                                   2 * defl, r.ra_um))
    Re = load_json("materials.json")["kienzle"][p.material]["Re_MPa"]
    stress = fe.clamp_stress_per_N("fin", nj, ch.half_angle) * F_high / Re
    return StrategyResult(p.pid, ch.name, scheme, F_high, F_low if scheme == "two-stage" else F_high, gh, gl, feasible, res, feats,
                          t_total + ch.setup_min * 60 / batch, ch.setup_min, min_grip, stress, notes)
