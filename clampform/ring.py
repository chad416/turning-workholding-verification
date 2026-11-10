"""Thin circular ring under equally spaced radial jaw loads: closed-form Fourier solution.

For a thin inextensional ring (mean radius R, bending stiffness EI) under a radial line load q(theta) =
sum q_k cos(k theta), each harmonic k >= 2 gives a radial displacement

    w_k = q_k R^4 / (EI (k^2 - 1)^2)

(curved-beam theory; e.g. Timoshenko & Goodier ring problems, Roark's Formulas for Stress and Strain, ch. 9).
The k = 0 part is the uniform (extensional) shrink w_0 = q_0 R^2 / (E A); k = 1 is a rigid translation and is
absent when the jaws balance. n equal jaws, each with total force P spread over +-alpha, excite only
k = n, 2n, ...:  q_k = (n P / (pi R)) * sin(k alpha) / (k alpha).

Positive w is inward (towards the axis), in the direction of the jaw force.
"""

from __future__ import annotations

import numpy as np


def ring_w(theta: np.ndarray, n_jaws: int, P: float, R: float, E: float, b: float, t: float,
           half_angle: float = 0.0, m_max: int = 60) -> np.ndarray:
    """Radial inward displacement (mm) of a thin rectangular-section ring (width b, thickness t)."""
    I = b * t**3 / 12
    A = b * t
    th = np.asarray(theta, float)
    w = np.full_like(th, n_jaws * P / (2 * np.pi * R) * R**2 / (E * A))
    for m in range(1, m_max + 1):
        k = m * n_jaws
        f = np.sin(k * half_angle) / (k * half_angle) if half_angle > 0 else 1.0
        qk = n_jaws * P / (np.pi * R) * f
        w = w + qk * R**4 / (E * I * (k * k - 1) ** 2) * np.cos(k * th)
    return w


def roark_two_point_dD(P: float, R: float, E: float, I: float) -> float:
    """Roark: thin ring, two equal opposite point loads P: decrease of the loaded diameter = 0.1488 P R^3 / (E I)
    (exact coefficient (pi^2 - 8) / (4 pi) = 0.14878). Bending only."""
    return (np.pi**2 - 8) / (4 * np.pi) * P * R**3 / (E * I)


def harmonic_amplitude_ratio(n_a: int, n_b: int, half_a: float = 0.0, half_b: float = 0.0) -> float:
    """Ratio of the first lobing harmonic amplitude of chuck b to chuck a at equal TOTAL clamping force.
    w_n ~ (sum of jaw forces) * f(n alpha) / (n^2 - 1)^2."""
    fa = np.sin(n_a * half_a) / (n_a * half_a) if half_a > 0 else 1.0
    fb = np.sin(n_b * half_b) / (n_b * half_b) if half_b > 0 else 1.0
    return (fb / (n_b**2 - 1) ** 2) / (fa / (n_a**2 - 1) ** 2)
