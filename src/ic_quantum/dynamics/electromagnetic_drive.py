"""Near-resonant coherent electromagnetic drive of an effective two-level system.

The source is an external coherent electromagnetic wave.  The platform-specific
electric/magnetic dipole matrix element is not guessed: it is absorbed into the
effective Rabi rate Omega.

H_RWA/hbar = 1/2 [Delta sigma_z
                  + Omega(cos(phi) sigma_x + sin(phi) sigma_y)].
"""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.validation import validate_unitary
from ic_quantum.dynamics.closed_system import apply_unitary, unitary_from_hamiltonian


def em_rwa_hamiltonian(
    rabi_rate: float,
    detuning: float,
    phase: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if hbar <= 0:
        raise ValueError("hbar must be positive.")
    omega = float(rabi_rate)
    if omega < 0:
        raise ValueError("rabi_rate must be non-negative.")
    delta = float(detuning)
    phi = float(phase)
    hamiltonian = 0.5 * hbar * (
        delta * SIGMA_Z
        + omega * (np.cos(phi) * SIGMA_X + np.sin(phi) * SIGMA_Y)
    )
    if not np.allclose(
        hamiltonian, hamiltonian.conjugate().T, atol=1e-12, rtol=0.0
    ):
        raise RuntimeError("Electromagnetic RWA Hamiltonian is not Hermitian.")
    return hamiltonian


def em_drive_unitary(
    rabi_rate: float,
    detuning: float,
    phase: float,
    time: float,
    hbar: float = 1.0,
) -> np.ndarray:
    if time < 0:
        raise ValueError("time must be non-negative.")
    unitary = unitary_from_hamiltonian(
        em_rwa_hamiltonian(rabi_rate, detuning, phase, hbar=hbar),
        time=float(time),
        hbar=hbar,
    )
    validate_unitary(unitary)
    return unitary


def apply_em_drive(
    rho: np.ndarray,
    *,
    rabi_rate: float,
    detuning: float,
    phase: float,
    time: float,
) -> np.ndarray:
    return apply_unitary(
        rho, em_drive_unitary(rabi_rate, detuning, phase, time)
    )
