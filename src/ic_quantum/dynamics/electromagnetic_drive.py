"""External coherent electromagnetic drive of an effective two-level system.

The implemented rotating-frame/RWA Hamiltonian is
H = hbar/2 [Delta sigma_z + Omega(cos(phi)sigma_x + sin(phi)sigma_y)].
Omega is the field-to-qubit coupling rate after the platform-specific dipole
matrix element has been absorbed into the effective coupling.
"""

from __future__ import annotations
import numpy as np
from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.dynamics.closed_system import unitary_from_hamiltonian, apply_unitary


def em_rwa_hamiltonian(rabi_rate: float, detuning: float, phase: float, hbar: float = 1.0) -> np.ndarray:
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    omega = float(rabi_rate)
    delta = float(detuning)
    phi = float(phase)
    return 0.5 * hbar * (
        delta * SIGMA_Z
        + omega * (np.cos(phi) * SIGMA_X + np.sin(phi) * SIGMA_Y)
    )


def em_drive_unitary(rabi_rate: float, detuning: float, phase: float, time: float, hbar: float = 1.0) -> np.ndarray:
    if time < 0:
        raise ValueError("time must be non-negative.")
    return unitary_from_hamiltonian(
        em_rwa_hamiltonian(rabi_rate, detuning, phase, hbar=hbar),
        time=float(time),
        hbar=hbar,
    )


def apply_em_drive(rho: np.ndarray, *, rabi_rate: float, detuning: float, phase: float, time: float) -> np.ndarray:
    return apply_unitary(rho, em_drive_unitary(rabi_rate, detuning, phase, time))
