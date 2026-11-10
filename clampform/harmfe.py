"""Fourier-harmonic axisymmetric finite elements: a body of revolution under loads that vary around the axis.

A turned part is a body of revolution, but the chuck jaws load it at n discrete angles. The displacement field is
expanded in circumferential harmonics (the symmetric set):

    u_r = sum_k U_k(r, z) cos(k theta),   u_z = sum_k W_k(r, z) cos(k theta),   u_theta = sum_k V_k(r, z) sin(k theta)

and each harmonic is an independent 2-D problem in the (r, z) section. This is the standard semi-analytical method
for axisymmetric solids under non-symmetric load (Zienkiewicz, Taylor & Zhu, The Finite Element Method, vol. 1,
chapter "Semi-analytical finite element processes"; Cook, Malkus, Plesha & Witt, Concepts and Applications of
Finite Element Analysis, 4th ed., section on axisymmetric solids under general loading). For n equal jaws only the
harmonics k = 0, n, 2n, ... are excited, so a 3-jaw chuck needs k = 0, 3, 6, ...

Elements: 8-node serendipity quadrilaterals (Q8) on a rectangular cell mesh of the section, 3 x 3 Gauss points.
Q8 represents linear bending through the wall exactly, so two or three elements across a thin wall are enough;
the tests check this against thin-ring theory, Lame and Roark's two-point-load ring.

The theta integral (pi for k >= 1, 2 pi for k = 0) multiplies the stiffness and the load alike and is left out.
Units: mm, N, MPa.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

# Gauss points
_G3 = np.array([-np.sqrt(0.6), 0.0, np.sqrt(0.6)])
_W3 = np.array([5 / 9, 8 / 9, 5 / 9])
# Q8 node order: corners (-1,-1) (1,-1) (1,1) (-1,1), then midsides (0,-1) (1,0) (0,1) (-1,0)
_XI = np.array([-1, 1, 1, -1, 0, 1, 0, -1], float)
_ETA = np.array([-1, -1, 1, 1, -1, 0, 1, 0], float)
_EDGES = ((0, 4, 1), (1, 5, 2), (2, 6, 3), (3, 7, 0))


def _shape(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    N = np.empty(8)
    dxi = np.empty(8)
    deta = np.empty(8)
    for i in range(8):
        a, b = _XI[i], _ETA[i]
        if i < 4:
            N[i] = 0.25 * (1 + a * xi) * (1 + b * eta) * (a * xi + b * eta - 1)
            dxi[i] = 0.25 * a * (1 + b * eta) * (2 * a * xi + b * eta)
            deta[i] = 0.25 * b * (1 + a * xi) * (a * xi + 2 * b * eta)
        elif a == 0:
            N[i] = 0.5 * (1 - xi * xi) * (1 + b * eta)
            dxi[i] = -xi * (1 + b * eta)
            deta[i] = 0.5 * b * (1 - xi * xi)
        else:
            N[i] = 0.5 * (1 + a * xi) * (1 - eta * eta)
            dxi[i] = 0.5 * a * (1 - eta * eta)
            deta[i] = -eta * (1 + a * xi)
    return N, dxi, deta


@dataclass
class Mesh:
    nodes: np.ndarray  # (N, 2): r, z
    elems: np.ndarray  # (E, 8) node indices, Q8 order
    rlines: np.ndarray = field(default_factory=lambda: np.zeros(0))
    zlines: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def n_nodes(self) -> int:
        return len(self.nodes)


def _lines(bounds: list[float], h: float) -> np.ndarray:
    b = np.unique(np.round(np.asarray(bounds, float), 6))
    out = [b[0]]
    for lo, hi in zip(b[:-1], b[1:]):
        n = max(1, int(np.ceil((hi - lo) / h - 1e-9)))
        out.extend(np.linspace(lo, hi, n + 1)[1:])
    return np.array(out)


def build_mesh(rects: list[tuple[float, float, float, float]], h: float, extra_z: list[float] | None = None,
               extra_r: list[float] | None = None, voids: list[tuple[float, float, float, float]] | None = None) -> Mesh:
    """Mesh the union of rectangles (r0, r1, z0, z1), minus the void rectangles, with Q8 cells of size <= h.
    All rectangle edges (and extra_z / extra_r, e.g. jaw and tool patch limits) become mesh lines."""
    voids = list(voids or [])
    rb = [v for R in rects for v in R[:2]] + [v for R in voids for v in R[:2]] + list(extra_r or [])
    zb = [v for R in rects for v in R[2:]] + [v for R in voids for v in R[2:]] + list(extra_z or [])
    rlo, rhi = min(R[0] for R in rects), max(R[1] for R in rects)
    rb = [min(max(v, rlo), rhi) for v in rb]
    rl, zl = _lines(rb, h), _lines(zb, h)
    key: dict[tuple[int, int], int] = {}
    nodes: list[tuple[float, float]] = []

    def nid(r: float, z: float) -> int:
        k = (int(round(r * 1e5)), int(round(z * 1e5)))
        if k not in key:
            key[k] = len(nodes)
            nodes.append((r, z))
        return key[k]

    elems = []
    for i in range(len(rl) - 1):
        for j in range(len(zl) - 1):
            r0, r1, z0, z1 = rl[i], rl[i + 1], zl[j], zl[j + 1]
            rc, zc = 0.5 * (r0 + r1), 0.5 * (z0 + z1)
            if not any(R[0] < rc < R[1] and R[2] < zc < R[3] for R in rects):
                continue
            if any(R[0] < rc < R[1] and R[2] < zc < R[3] for R in voids):
                continue
            rm, zm = 0.5 * (r0 + r1), 0.5 * (z0 + z1)
            elems.append([nid(r0, z0), nid(r1, z0), nid(r1, z1), nid(r0, z1), nid(rm, z0), nid(r1, zm), nid(rm, z1), nid(r0, zm)])
    return Mesh(np.array(nodes), np.array(elems, int), rl, zl)


def elasticity(E: float, nu: float) -> np.ndarray:
    """Isotropic D for strain order (e_r, e_z, e_theta, g_rz, g_rtheta, g_ztheta)."""
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[0, 0] = D[1, 1] = D[2, 2] = lam + 2 * mu
    D[3, 3] = D[4, 4] = D[5, 5] = mu
    return D


class HarmonicModel:
    """Linear elastic body of revolution; solve one circumferential harmonic at a time."""

    def __init__(self, mesh: Mesh, E: float = 210e3, nu: float = 0.3):
        self.mesh, self.E, self.nu = mesh, E, nu
        self.D = elasticity(E, nu)
        # precompute shape data at the 9 Gauss points of every element
        X = mesh.nodes[mesh.elems]  # (E, 8, 2)
        Ns, dNr, dNz, wr = [], [], [], []
        for a, wa in zip(_G3, _W3):
            for b, wb in zip(_G3, _W3):
                N, dxi, deta = _shape(a, b)
                J11 = X[:, :, 0] @ dxi  # dr/dxi
                J12 = X[:, :, 1] @ dxi  # dz/dxi
                J21 = X[:, :, 0] @ deta
                J22 = X[:, :, 1] @ deta
                det = J11 * J22 - J12 * J21
                # inverse Jacobian: [dxi/dr dxi/dz; deta/dr deta/dz]
                dNdr = (J22[:, None] * dxi[None, :] - J12[:, None] * deta[None, :]) / det[:, None]
                dNdz = (-J21[:, None] * dxi[None, :] + J11[:, None] * deta[None, :]) / det[:, None]
                r = X[:, :, 0] @ N
                Ns.append(np.broadcast_to(N, (len(X), 8)))
                dNr.append(dNdr)
                dNz.append(dNdz)
                wr.append(det * wa * wb * r)
        self._N = np.stack(Ns, 1)  # (E, 9, 8)
        self._dNr = np.stack(dNr, 1)
        self._dNz = np.stack(dNz, 1)
        self._wr = np.stack(wr, 1)  # (E, 9)
        self._r = np.einsum("egi,ei->eg", self._N, X[:, :, 0])

    # --- B matrices -------------------------------------------------------------------------------------------
    def _B(self, k: int) -> np.ndarray:
        """(E, 9, nstrain, ndof_e) strain-displacement matrices for harmonic k."""
        N, Nr, Nz, r = self._N, self._dNr, self._dNz, self._r[:, :, None]
        E9 = N.shape[:2]
        if k == 0:
            B = np.zeros(E9 + (4, 16))
            B[:, :, 0, 0::2] = Nr
            B[:, :, 1, 1::2] = Nz
            B[:, :, 2, 0::2] = N / r
            B[:, :, 3, 0::2] = Nz
            B[:, :, 3, 1::2] = Nr
            return B
        B = np.zeros(E9 + (6, 24))
        B[:, :, 0, 0::3] = Nr
        B[:, :, 1, 1::3] = Nz
        B[:, :, 2, 0::3] = N / r
        B[:, :, 2, 2::3] = k * N / r
        B[:, :, 3, 0::3] = Nz
        B[:, :, 3, 1::3] = Nr
        B[:, :, 4, 0::3] = -k * N / r
        B[:, :, 4, 2::3] = Nr - N / r
        B[:, :, 5, 1::3] = -k * N / r
        B[:, :, 5, 2::3] = Nz
        return B

    def ndof(self, k: int) -> int:
        return 2 if k == 0 else 3

    def stiffness(self, k: int) -> sp.csr_matrix:
        D = self.D if k else self.D[:4, :4]
        B = self._B(k)
        Ke = np.empty((B.shape[0], B.shape[3], B.shape[3]))
        for i0 in range(0, B.shape[0], 400):  # element chunks keep the temporaries small
            Bc = B[i0:i0 + 400]
            DB = np.einsum("st,egtj->egsj", D, Bc)
            Ke[i0:i0 + 400] = np.einsum("egsi,egsj,eg->eij", Bc, DB, self._wr[i0:i0 + 400])
        del B
        nd = self.ndof(k)
        dofs = (self.mesh.elems[:, :, None] * nd + np.arange(nd)[None, None, :]).reshape(len(self.mesh.elems), -1)
        rows = np.repeat(dofs, dofs.shape[1], axis=1).ravel()
        cols = np.tile(dofs, (1, dofs.shape[1])).ravel()
        n = self.mesh.n_nodes * nd
        return sp.coo_matrix((Ke.ravel(), (rows, cols)), shape=(n, n)).tocsr()

    # --- loads ------------------------------------------------------------------------------------------------
    def _vertical_edges(self) -> np.ndarray:
        """All element edges of constant r: rows (n0, nmid, n1, r, zmin, zmax)."""
        if not hasattr(self, "_vedges"):
            X = self.mesh.nodes
            rows = []
            for ed in _EDGES:
                nn = self.mesh.elems[:, list(ed)]
                rr = X[nn, 0]
                ok = np.abs(rr[:, 0] - rr[:, 2]) < 1e-9
                zz = X[nn, 1]
                rows.append(np.column_stack([nn[ok], rr[ok, 0], zz[ok].min(1), zz[ok].max(1)]))
            self._vedges = np.vstack(rows)
        return self._vedges

    def surface_load(self, k: int, r_s: float, z0: float, z1: float, q: float, comp: int = 0) -> np.ndarray:
        """Nodal loads for a traction amplitude q (MPa) on the cylindrical surface r = r_s, z in [z0, z1].
        comp: 0 radial, 1 axial, 2 circumferential (k >= 1)."""
        nd = self.ndof(k)
        F = np.zeros(self.mesh.n_nodes * nd)
        X = self.mesh.nodes
        tol = 1e-6
        E = self._vertical_edges()
        sel = E[(np.abs(E[:, 3] - r_s) < tol) & (E[:, 4] >= z0 - tol) & (E[:, 5] <= z1 + tol)]
        # an edge on the surface appears once per element; boundary edges belong to one element only
        for row in sel:
            nn = row[:3].astype(int)
            za, zb = X[nn[0], 1], X[nn[2], 1]
            jac = abs(zb - za) / 2
            for s, w in zip(_G3, _W3):
                Nl = np.array([0.5 * s * (s - 1), 1 - s * s, 0.5 * s * (s + 1)])
                F[nn * nd + comp] += Nl * q * r_s * w * jac
        return F

    # --- solve ------------------------------------------------------------------------------------------------
    def solve(self, k: int, F: np.ndarray, fixed_nodes: np.ndarray | None = None) -> np.ndarray:
        """Solve harmonic k for one load vector (n,) or several (n, m). fixed_nodes: all DOF of these nodes held
        (e.g. a fully gripped zone). Without supports, k = 0 gets its axial rigid motion removed at one node;
        k >= 2 needs no support. Nothing is cached: one factorisation per call keeps memory flat."""
        nd = self.ndof(k)
        K = self.stiffness(k)
        if fixed_nodes is not None and len(fixed_nodes):
            fixed = (np.asarray(fixed_nodes, int)[:, None] * nd + np.arange(nd)).ravel()
        elif k == 0:
            fixed = np.array([int(np.argmin(self.mesh.nodes[:, 1])) * nd + 1])
        elif k == 1:
            raise ValueError("harmonic 1 contains rigid-body motion: give fixed_nodes")
        else:
            fixed = np.zeros(0, int)
        free = np.setdiff1d(np.arange(K.shape[0]), fixed)
        lu = spla.splu(K[free][:, free].tocsc())
        del K
        F2 = F if F.ndim == 2 else F[:, None]
        u = np.zeros((F2.shape[0], F2.shape[1]))
        u[free] = lu.solve(np.ascontiguousarray(F2[free]))
        del lu
        if F.ndim == 1:
            return u[:, 0].reshape(-1, nd)
        return u.T.reshape(F2.shape[1], -1, nd)

    def stresses(self, k: int, u: np.ndarray) -> np.ndarray:
        """Stress amplitudes at element centroids (E, 6); cos-type rows 0-3, sin-type rows 4-5."""
        B = self._B(k)
        nd = self.ndof(k)
        ue = u.reshape(-1)[(self.mesh.elems[:, :, None] * nd + np.arange(nd)).reshape(len(self.mesh.elems), -1)]
        eps = np.einsum("egsi,ei->egs", B, ue).mean(1)
        D = self.D if k else self.D[:4, :4]
        s = eps @ D.T
        if k == 0:
            s = np.hstack([s, np.zeros((len(s), 2))])
        return s

    def nodes_on(self, r: float, z0: float, z1: float, tol: float = 1e-6) -> np.ndarray:
        X = self.mesh.nodes
        return np.where((np.abs(X[:, 0] - r) < tol) & (X[:, 1] >= z0 - tol) & (X[:, 1] <= z1 + tol))[0]


def jaw_harmonics(n_jaws: int, half_angle: float, k_max: int) -> list[tuple[int, float]]:
    """(k, c_k) such that the radial pressure of n equal jaws, each spreading a unit total force over
    an arc of +-half_angle (rad), is p(theta) = sum_k c_k cos(k theta) / (r_s * L) per unit jaw force.
    Only k = 0, n, 2n, ... are excited (Fourier series of n equally spaced arc loads)."""
    out = [(0, n_jaws / (2 * np.pi))]
    k = n_jaws
    while k <= k_max:
        f = np.sin(k * half_angle) / (k * half_angle) if half_angle > 0 else 1.0
        out.append((k, n_jaws / np.pi * f))
        k += n_jaws
    return out
