"""Part definitions (gland, piston), ISO 286 limits, and the section geometry at each machining stage."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ISO 286-1 standard tolerance grades IT6-IT11 (um) for the size bands used here, and the fundamental deviation of
# shaft position f (es, um). Quoted from memory of the ISO 286-1 tables; tests/test_parts.py checks them against
# the standard tolerance unit i = 0.45 D^(1/3) + 0.001 D (IT7 = 16 i, IT8 = 25 i, IT9 = 40 i, IT11 = 100 i).
_BANDS = [  # (upper limit of band, {grade: um}, es_f)
    (50, {6: 16, 7: 25, 8: 39, 9: 62, 10: 100, 11: 160}, -25),
    (80, {6: 19, 7: 30, 8: 46, 9: 74, 10: 120, 11: 190}, -30),
    (120, {6: 22, 7: 35, 8: 54, 9: 87, 10: 140, 11: 220}, -36),
    (180, {6: 25, 7: 40, 8: 63, 9: 100, 10: 160, 11: 250}, -43),
    (250, {6: 29, 7: 46, 8: 72, 9: 115, 10: 185, 11: 290}, -50),
]
_LOWER = {50: 30, 80: 50, 120: 80, 180: 120, 250: 180}


def it_grade(d: float, grade: int) -> int:
    for up, it, _ in _BANDS:
        if _LOWER[up] < d <= up:
            return it[grade]
    raise ValueError(f"size {d} mm outside the tabulated bands 30-250 mm")


def limits(d: float, fit: str) -> tuple[float, float]:
    """(lower, upper) deviation in um for 'H7', 'f7', 'h9' ... (only H, h, f positions are needed here)."""
    pos, g = fit[0], int(fit[1:])
    it = it_grade(d, g)
    if pos == "H":
        return 0.0, float(it)
    if pos == "h":
        return -float(it), 0.0
    if pos == "f":
        es = next(e for up, _, e in _BANDS if _LOWER[up] < d <= up)
        return float(es - it), float(es)
    raise ValueError(fit)


@dataclass
class Feature:
    name: str
    side: str  # "od" or "id"
    d: float  # finished diameter (mm)
    z0: float  # axial range (z <= 0 into the part)
    z1: float
    fit: str | None
    ra_um: float
    kind: str  # "diameter" or "groove"
    tol_um: float = 0.0  # IT width of the fit (0 if no fit)

    @property
    def r(self) -> float:
        return self.d / 2


@dataclass
class Part:
    pid: str
    family: str
    order: str
    material: str
    od: float
    bore: float
    length: float
    grooves: list[dict]
    od_fit: str | None
    od_nominal: float
    od_ra: float
    bore_fit: str | None
    bore_ra: float
    stock_od: float
    stock_id: float
    counterbore: dict | None = None
    features: list[Feature] = field(default_factory=list)

    # machining allowances and the clamp zone behind the part (assumed layout: part, 6 mm part-off/clearance, grip)
    over_end: float = 3.0  # OD/ID finishing runs this far past the part end into the part-off zone
    gap: float = 6.0

    @property
    def is_tube(self) -> bool:
        return self.family == "tube"

    def grip(self, grip_len: float) -> tuple[float, float]:
        """Axial range of the jaws. Bar work (gland, piston): on the bar behind the part, beyond the part-off.
        Tube: on the tube OD, behind the machined mouth features (clearance 10 mm for the tool)."""
        if self.is_tube:
            z1 = -self.counterbore["depth"] - 10.0
            return z1 - grip_len, z1
        z1 = -self.length - self.gap
        return z1 - grip_len, z1

    @property
    def grip_r(self) -> float:
        return self.od / 2 if self.is_tube else self.stock_od / 2

    def zmin(self, grip_len: float) -> float:
        return self.grip(grip_len)[0]

    def rects(self, stage: str, grip_len: float) -> tuple[list, list]:
        if self.is_tube:
            cb = self.counterbore
            mat = [(self.bore / 2, self.od / 2, -self.length, 0.0)]
            voids = [] if stage == "A" else [(self.bore / 2 - 1, cb["d"] / 2, -cb["depth"], 0.0)]
            return mat, voids
        """Material rectangles and voids (r0, r1, z0, z1) of the section at a stage:
        'A'   = OD finished, bore still the stock bore (where the usual sequence finishes the OD);
        'fin' = everything finished except the part-off (where bores and grooves are finished)."""
        rs_o, rs_i = self.stock_od / 2, self.stock_id / 2
        zb = self.zmin(grip_len)
        L = self.length
        mat = [(rs_i, rs_o, zb, -L - self.over_end), (rs_i, self.od / 2, -L - self.over_end, 0.0)]
        voids: list[tuple[float, float, float, float]] = []
        if stage == "A":
            return mat, voids
        mat = [(rs_i, rs_o, zb, -L - self.over_end), (self.bore / 2, self.od / 2, -L - self.over_end, 0.0)]
        for g in self.grooves:
            za, zc = -g["z"] - g["width"], -g["z"]
            if g["side"] == "id":
                voids.append((self.bore / 2 - 1, g["bottom_d"] / 2, za, zc))
            else:
                voids.append((g["bottom_d"] / 2, self.od / 2 + 1, za, zc))
        return mat, voids


def _features(p: Part) -> list[Feature]:
    feats = []
    tol = (lambda d, fit: (limits(d, fit)[1] - limits(d, fit)[0]) if fit else 0.0)
    if p.is_tube:
        cb = p.counterbore
        return [Feature("gland-seat counterbore", "id", cb["d"], -cb["depth"], 0.0, cb["fit"], cb["ra_um"], "diameter", tol(cb["d"], cb["fit"]))]
    od_grooves = [(-g["z"] - g["width"], -g["z"]) for g in p.grooves if g["side"] == "od"]
    tol = (lambda d, fit: (limits(d, fit)[1] - limits(d, fit)[0]) if fit else 0.0)
    feats.append(Feature("OD", "od", p.od, -p.length, 0.0, p.od_fit, p.od_ra, "diameter", tol(p.od_nominal, p.od_fit)))
    feats.append(Feature("bore", "id", p.bore, -p.length, 0.0, p.bore_fit, p.bore_ra, "diameter", tol(p.bore, p.bore_fit)))
    for g in p.grooves:
        feats.append(Feature(g["name"], g["side"], g["bottom_d"], -g["z"] - g["width"], -g["z"], g["fit"], g["ra_um"], "groove",
                             tol(g["bottom_d"], g["fit"])))
    _ = od_grooves
    return feats


def load_parts(path: Path | None = None) -> dict[str, Part]:
    d = json.loads((path or DATA / "parts.json").read_text(encoding="utf-8"))
    out = {}
    for pid, v in d["parts"].items():
        p = Part(pid, v["family"], v["order"], v["material"], v["od"], v["bore"], v["length"], v["grooves"], v["od_fit"],
                 v["od_nominal"], v["od_ra_um"], v["bore_fit"], v["bore_ra_um"], v["stock"]["od"], v["stock"]["id"],
                 v.get("counterbore"))
        p.features = _features(p)
        out[pid] = p
    return out


def load_json(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))
