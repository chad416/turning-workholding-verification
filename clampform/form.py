"""Form error of a turned feature: the part is cut round while the jaws squeeze it, and springs back when released.

A surface point that is cut while displaced by u_r(theta) ends, after release, at r(theta) = R_cut - u_r(theta)
(linear elasticity, no residual stress from cutting). So the released profile is the mirror image of the clamped
deformation of the section *as it was when that surface was finished*. The deformation comes from the harmonic FE
model (harmfe.py); the clamping force enters linearly, so everything is computed per newton of jaw force.

Profile measures (ISO 12181 terms): roundness RONt about the least-squares circle; the two-point size range (what
a micrometer or a two-point bore gauge sees); the minimum circumscribed / maximum inscribed circle (what the
mating part sees, and what the envelope requirement of ISO 14405-1 limits); and the reading of a V-block gauge.

A profile with only odd lobes (3, 9, ...) has a constant two-point size: a micrometer cannot see it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .harmfe import HarmonicModel, build_mesh, jaw_harmonics
from .parts import Feature, Part

N_THETA = 360
THETA = np.linspace(0, 2 * np.pi, N_THETA, endpoint=False)


@dataclass
class ProfileMetrics:
    ron: float  # roundness, peak to valley about the LS circle (mm)
    two_point_range: float  # max - min two-point size (mm)
    size_shift: float  # change of the mean diameter after release (mm, + = larger)
    mcc_excess: float  # minimum circumscribed radius - LS radius (mm)
    mic_deficit: float  # LS radius - maximum inscribed radius (mm)


def metrics(r: np.ndarray, R_nom: float) -> ProfileMetrics:
    a = 2 * np.mean(r * np.cos(THETA))
    b = 2 * np.mean(r * np.sin(THETA))
    R0 = np.mean(r)
    dev = r - R0 - a * np.cos(THETA) - b * np.sin(THETA)
    half = N_THETA // 2
    tp = r[:half] + r[half:]
    return ProfileMetrics(float(dev.max() - dev.min()), float(tp.max() - tp.min()), float(2 * (R0 - R_nom)),
                          float(dev.max()), float(-dev.min()))


def vblock_reading(dev: np.ndarray, included_deg: float) -> float:
    """Range of the indicator reading when the profile (deviation from a circle, sampled on THETA) is rotated in a
    V-block of the given included angle, indicator on the bisector opposite the vee (small-deviation kinematics:
    the centre moves so that both flanks stay in contact)."""
    beta = math.radians(included_deg / 2)
    psi = np.array([-math.pi / 2 + beta, -math.pi / 2 - beta])  # directions of the two contact points
    nvec = np.stack([np.cos(psi), np.sin(psi)], 1)
    Minv = np.linalg.inv(nvec)
    reads = []
    for phi in THETA:
        d = np.interp((psi - phi) % (2 * np.pi), THETA, dev, period=2 * np.pi)
        c = Minv @ (-d)
        top = np.interp((math.pi / 2 - phi) % (2 * np.pi), THETA, dev, period=2 * np.pi)
        reads.append(c[1] + top)
    reads = np.array(reads)
    return float(reads.max() - reads.min())


def two_point_reading(dev: np.ndarray) -> float:
    half = len(dev) // 2
    tp = dev[:half] + dev[half:]
    return float(tp.max() - tp.min())


class PartFE:
    """Harmonic FE of one part at its machining stages, with unit jaw-load and unit tool-load responses."""

    def __init__(self, part: Part, grip_len: float, h: float | None = None, k_max: int = 48, E: float = 210e3, nu: float = 0.3):
        self.part, self.grip_len, self.k_max = part, grip_len, k_max
        id_bottoms = [g["bottom_d"] for g in part.grooves if g["side"] == "id"] + ([part.counterbore["d"]] if part.counterbore else [])
        od_bottoms = [g["bottom_d"] for g in part.grooves if g["side"] == "od"]
        wall = min((part.od - max(id_bottoms or [part.bore])) / 2, (min(od_bottoms or [part.od]) - part.bore) / 2)
        self.h = h or float(np.clip(wall / 3, 0.6, 2.0))
        self.models: dict[str, HarmonicModel] = {}
        self._jaw: dict[tuple[str, int], np.ndarray] = {}
        self._tool: dict[tuple[str, int], object] = {}
        zg0, zg1 = part.grip(grip_len)
        self.grip_z = (zg0, zg1)
        self.r_grip = part.grip_r
        ez = [zg0, zg1]
        for f in part.features:
            zc = 0.5 * (f.z0 + f.z1)
            ez += [zc - 1.5, zc + 1.5]
        for stage in ("A", "fin"):
            mat, voids = part.rects(stage, grip_len)
            mesh = build_mesh(mat, self.h, extra_z=ez, voids=voids)
            self.models[stage] = HarmonicModel(mesh, E, nu)

    # --- clamping ---------------------------------------------------------------------------------------------
    def _jaw_k(self, stage: str, k: int) -> np.ndarray:
        key = (stage, k)
        if key not in self._jaw:
            M = self.models[stage]
            F = M.surface_load(k, self.r_grip, *self.grip_z, q=-1.0)  # 1 MPa inward traction amplitude
            self._jaw[key] = M.solve(k, F)
        return self._jaw[key]

    def clamp_response(self, stage: str, n_jaws: int, half_angle: float, nodes: np.ndarray) -> np.ndarray:
        """u_r(theta) at the given nodes for 1 N per jaw: array (len(nodes), N_THETA)."""
        out = np.zeros((len(nodes), N_THETA))
        area = self.r_grip * (self.grip_z[1] - self.grip_z[0])
        for k, c in jaw_harmonics(n_jaws, half_angle, self.k_max):
            if k % 3:
                continue
            U = self._jaw_k(stage, k)[nodes, 0] * (c / area)
            out += U[:, None] * np.cos(k * THETA)[None, :]
        return out

    def feature_nodes(self, f: Feature, stage: str) -> np.ndarray:
        M = self.models[stage]
        nn = M.nodes_on(f.r, f.z0, f.z1)
        if not len(nn):
            raise ValueError(f"no nodes on {f.name} at r={f.r} in stage {stage}")
        return nn

    def feature_profile(self, f: Feature, stage: str, n_jaws: int, half_angle: float, F_jaw_total: float) -> tuple[np.ndarray, ProfileMetrics]:
        """Released profile of the worst section of a feature finished at total jaw force F (N)."""
        nn = self.feature_nodes(f, stage)
        u = self.clamp_response(stage, n_jaws, half_angle, nn) * (F_jaw_total / n_jaws)
        best = None
        for i in range(len(nn)):
            r = f.r - u[i]
            m = metrics(r, f.r)
            if best is None or m.ron > best[1].ron:
                best = (r - np.mean(r), m)
        return best

    def clamp_stress_per_N(self, stage: str, n_jaws: int, half_angle: float) -> float:
        """Largest von Mises stress (element centroids, MPa) per newton of total jaw force."""
        key = ("stress", stage, n_jaws, round(half_angle, 6))
        if key not in self._tool:
            self._tool[key] = self._clamp_stress(stage, n_jaws, half_angle)
        return self._tool[key]

    def _clamp_stress(self, stage: str, n_jaws: int, half_angle: float) -> float:
        M = self.models[stage]
        area = self.r_grip * (self.grip_z[1] - self.grip_z[0])
        th = np.linspace(0, np.pi / n_jaws, 13)
        s = np.zeros((len(M.mesh.elems), 6, len(th)))
        for k, c in jaw_harmonics(n_jaws, half_angle, self.k_max):
            if k % 3:
                continue
            sk = M.stresses(k, self._jaw_k(stage, k)) * (c / area)
            cos, sin = np.cos(k * th), np.sin(k * th)
            s[:, :4, :] += sk[:, :4, None] * cos[None, None, :]
            s[:, 4:, :] += sk[:, 4:, None] * sin[None, None, :]
        sr, sz, st, trz, trt, tzt = (s[:, i, :] for i in range(6))
        vm = np.sqrt(0.5 * ((sr - sz) ** 2 + (sz - st) ** 2 + (st - sr) ** 2) + 3 * (trz**2 + trt**2 + tzt**2))
        return float(vm.max() / n_jaws)

    # --- tool load ----------------------------------------------------------------------------------------------
    def tool_compliance(self, f: Feature, stage: str, k_max: int = 24, half_angle: float = math.radians(2.0)) -> float:
        """Radial displacement (mm/N) at the middle of a feature under a radial point-like tool load, with the grip
        zone held (all displacements zero on the gripped surface). Used for the size error of the cut. All features
        of a stage are solved together (one factorisation per harmonic)."""
        key = (f.name, stage)
        if key not in self._tool:
            self._tool_all(stage, k_max, half_angle)
        return self._tool[key]

    def _tool_all(self, stage: str, k_max: int, half_angle: float) -> None:
        M = self.models[stage]
        X = M.mesh.nodes
        zg0, zg1 = self.grip_z
        fixed = np.where((np.abs(X[:, 0] - self.r_grip) < 1e-6) & (X[:, 1] >= zg0 - 1e-6) & (X[:, 1] <= zg1 + 1e-6))[0]
        cases = []
        for f in self.part.features:
            zc = 0.5 * (f.z0 + f.z1)
            za, zb = zc - 1.5, zc + 1.5
            nn = M.nodes_on(f.r, za, zb)
            if not len(nn):  # groove narrower than the patch: load the groove bottom
                za, zb = f.z0, f.z1
                nn = M.nodes_on(f.r, za, zb)
            if not len(nn):
                continue
            centre = nn[np.argmin(np.abs(X[nn, 1] - zc))]
            sign = 1.0 if f.side == "od" else -1.0  # tool pushes the OD inward, the bore outward
            cases.append((f.name, za, zb, centre, sign, f.r * (zb - za), f.r))
        w = np.zeros(len(cases))
        for k in range(0, k_max + 1):
            c = (1 / (2 * np.pi)) if k == 0 else (1 / np.pi) * (np.sin(k * half_angle) / (k * half_angle))
            F = np.stack([M.surface_load(k, r, za, zb, q=-sg * c / area) for _, za, zb, _, sg, area, r in cases], 1)
            u = M.solve(k, F, fixed_nodes=fixed)
            w += np.array([u[i, cs[3], 0] for i, cs in enumerate(cases)])
        for i, cs in enumerate(cases):
            self._tool[(cs[0], stage)] = abs(w[i])
