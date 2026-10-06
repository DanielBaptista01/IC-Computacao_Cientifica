"""Coherent Zeeman coupling to an external magnetic field.

H_int = hbar*gamma/2 * B . sigma.
This is a generic effective-spin model; gamma and B must be supplied for the
platform of interest and are kept explicit rather than hidden in a channel label.
"""

from __future__ import annotations
import numpy as np
from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.dynamics.closed_system import unitary_from_hamiltonian, apply_unitary


def zeeman_hamiltonian(
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    gamma = float(gyromagnetic_ratio_rad_s_t)
    bx, by, bz = (float(v) for v in field_tesla)
    return 0.5 * hbar * gamma * (bx * SIGMA_X + by * SIGMA_Y + bz * SIGMA_Z)


def magnetic_field_unitary(
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    time: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if time < 0:
        raise ValueError("time must be non-negative.")
    return unitary_from_hamiltonian(
        zeeman_hamiltonian(field_tesla, gyromagnetic_ratio_rad_s_t, hbar=hbar),
        time=float(time),
        hbar=hbar,
    )


def apply_magnetic_field(
    rho: np.ndarray,
    *,
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    time: float,
) -> np.ndarray:
    return apply_unitary(
        rho,
        magnetic_field_unitary(field_tesla, gyromagnetic_ratio_rad_s_t, time),
    )
