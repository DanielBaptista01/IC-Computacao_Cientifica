"""Compatibility helper for coherent static/piecewise-constant Zeeman fields.

The authoritative physical-source family is external-magnetic-field-wave in
external_field.py.  This module preserves the static-vector API that was merged
into main while avoiding a second causal identity for the same source/mechanism.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.validation import validate_unitary
from ic_quantum.dynamics.closed_system import apply_unitary, unitary_from_hamiltonian


def zeeman_hamiltonian(
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    gamma = float(gyromagnetic_ratio_rad_s_t)
    if gamma < 0:
        raise ValueError("gyromagnetic_ratio_rad_s_t must be non-negative.")
    bx, by, bz = (float(v) for v in field_tesla)
    hamiltonian = 0.5 * hbar * gamma * (
        bx * SIGMA_X + by * SIGMA_Y + bz * SIGMA_Z
    )
    if not np.allclose(
        hamiltonian, hamiltonian.conjugate().T, atol=1e-12, rtol=0.0
    ):
        raise RuntimeError("Zeeman Hamiltonian is not Hermitian.")
    return hamiltonian


def magnetic_field_unitary(
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    time: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if time < 0:
        raise ValueError("time must be non-negative.")
    unitary = unitary_from_hamiltonian(
        zeeman_hamiltonian(
            field_tesla, gyromagnetic_ratio_rad_s_t, hbar=hbar
        ),
        time=float(time),
        hbar=hbar,
    )
    validate_unitary(unitary)
    return unitary


def apply_magnetic_field(
    rho: np.ndarray,
    *,
    field_tesla: tuple[float, float, float],
    gyromagnetic_ratio_rad_s_t: float,
    time: float,
) -> np.ndarray:
    return apply_unitary(
        rho,
        magnetic_field_unitary(
            field_tesla, gyromagnetic_ratio_rad_s_t, time
        ),
    )
