"""Write the lathe program of a part for a verified workholding strategy (FANUC or Sinumerik dialect).

What the workholding analysis puts into the program:
  * the two chuck-pressure presets as a set-up instruction in the header (static force in kN) and the M-codes that
    select them (builder-specific example codes from data/machine.json);
  * a spindle-speed limit per stage (FANUC G50 S / Sinumerik LIMS=) derived from the centrifugal loss of grip;
  * spindle stop + preset switch + dwell before the finishing stage (two-stage scheme);
  * a dwell of at least two revolutions at every groove bottom, so the thin wall springs back under the tool.
Moves are explicit G0/G1 (no canned cycles) so that the read-back verifier sees every cut.
Tool reference: nose centre for turning and boring (no G41/G42); grooving inserts reference their +Z corner and
extend towards -Z by the insert width.
"""

from __future__ import annotations

import math

from .parts import Part, load_json
from .process import StrategyResult, chuck_for, tools

SAFE_X, SAFE_Z = 220.0, 100.0


def _f(v: float) -> str:
    return f"{v:.3f}"


def write(p: Part, s: StrategyResult, dialect: str = "fanuc", prog_no: int = 3001) -> str:
    T = tools()
    lathe = load_json("machine.json")["lathe"]
    mc = lathe["clamp_mcodes"]
    fan = dialect == "fanuc"
    c = (lambda t: f"({t.upper()})") if fan else (lambda t: f"; {t}")
    L: list[str] = []
    if fan:
        L += ["%", f"O{prog_no} ({p.pid} {p.family.upper()} - WORKHOLDING VERIFIED)"]
    else:
        L += [f"; {p.pid} {p.family} - workholding verified"]
    L.append(c("simulated output - not proven on a machine"))
    L.append(c(f"stock D{p.stock_od:g} x D{p.stock_id:g} {p.material}" if not p.is_tube else f"tube D{p.od:g} x D{p.bore:g} {p.material}"))
    ch = chuck_for(p, s.chuck.split("-")[0])
    zg0, zg1 = p.grip(ch.grip_len)
    L.append(c(f"chuck {s.chuck} grip D{2 * p.grip_r:g} from Z{zg0:g} to Z{zg1:g}"))
    if s.scheme == "two-stage":
        L.append(c(f"clamp preset HIGH {s.F_high / 1e3:.1f} kN ({mc['high']}) / LOW {s.F_low / 1e3:.1f} kN ({mc['low']})"))
    else:
        L.append(c(f"clamp preset HIGH {s.F_high / 1e3:.1f} kN ({mc['high']}) - single pressure"))
    L.append(c(f"spindle limit rough {s.g50_high:.0f} rpm / finish {s.g50_low:.0f} rpm"))
    L.append("G21 G18 G40 G99 G97" if fan else "G18 G71 G90 G95 G97")
    L.append(f"{mc['high']} " + c("clamp preset high"))
    L.append("G4 X2.0" if fan else "G4 F2.0")
    cur_tool, cur_stage = None, "high"
    tool_no = {k: i + 1 for i, k in enumerate(sorted(T))}
    for r in s.ops:
        o = r.op
        stage = "low" if (s.scheme == "two-stage" and o.finish) else "high"
        g50 = s.g50_low if stage == "low" else s.g50_high
        if stage != cur_stage:
            L.append(f"G0 X{_f(SAFE_X)} Z{_f(SAFE_Z)}")
            L.append("M5")
            L.append(f"{mc['low']} " + c("clamp preset low"))
            L.append("G4 X2.0" if fan else "G4 F2.0")
            cur_stage, cur_tool = stage, None
        if o.tool != cur_tool:
            if cur_tool is not None:
                L += [f"G0 X{_f(SAFE_X)} Z{_f(SAFE_Z)} M9", "M5"]
            t = T[o.tool]
            n = tool_no[o.tool]
            L.append(f"G0 X{_f(SAFE_X)} Z{_f(SAFE_Z)}")
            L.append(f"T{n:02d}{n:02d} " + c(t["desc"]) if fan else f"T{n} D1 " + c(t["desc"]))
            L.append(f"G50 S{g50:.0f}" if fan else f"LIMS={g50:.0f}")
            L.append(f"G96 S{o.vc:.0f} M3")
            L.append("M8")
            cur_tool = o.tool
        L.append(c(o.name))
        w = T[o.tool].get("width", 0.0)
        if o.kind == "face":
            L += [f"G0 X{_f(o.d + 3)} Z{_f(2.0)}", f"G0 Z{_f(0.0)}", f"G1 X{_f(o.d_min_speed - 2)} F{o.f:.3f}", f"G0 Z{_f(2.0)}"]
        elif o.kind == "turn":
            L += [f"G0 X{_f(o.d)} Z{_f(2.0)}", f"G1 Z{_f(o.z0)} F{o.f:.3f}", f"G1 X{_f(o.d + 2)}", f"G0 Z{_f(2.0)}"]
        elif o.kind == "bore":
            L += [f"G0 X{_f(o.d)} Z{_f(2.0)}", f"G1 Z{_f(o.z0)} F{o.f:.3f}", f"G1 X{_f(o.d - 1)}", f"G0 Z{_f(2.0)}"]
        else:  # grooving
            inner = o.kind == "groove_int"
            start = (p.bore - 1) if inner else (p.od + 2)
            dw = math.ceil(max(2 * 60 / max(r.n, 1), 0.1) * 100) / 100 + 0.02
            dwell = f"G4 X{dw:.2f}" if fan else "G4 S2"
            if o.plunge:
                L += [f"G0 X{_f(start)} Z{_f(2.0)}", f"G0 Z{_f(o.z1)}", f"G1 X{_f(o.d)} F{o.f:.3f}", dwell, f"G1 X{_f(start)}", f"G0 Z{_f(2.0)}"]
            else:
                L += [f"G0 X{_f(start)} Z{_f(2.0)}", f"G0 Z{_f(o.z1)}", f"G1 X{_f(o.d)} F{T[o.tool]['f']:.3f}", dwell,
                      f"G1 Z{_f(o.z0 + w)} F{o.f:.3f}", dwell, f"G1 X{_f(start)}", f"G0 Z{_f(2.0)}"]
    L += [f"G0 X{_f(SAFE_X)} Z{_f(SAFE_Z)} M9", "M5", "M30"]
    if fan:
        L.append("%")
    return "\n".join(L) + "\n"
