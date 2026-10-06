"""Canonical coherent perturbation used as the positive reversibility control."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import SIGMA_Z
from ic_quantum.dynamics.closed_system import unitary_from_hamiltonian


def coherent_z_hamiltonian(omega: float, hbar: float = 1.0) -> np.ndarray:
    """H_A = (hbar * omega / 2) sigma_z."""
    return 0.5 * hbar * float(omega) * SIGMA_Z


def coherent_z_unitary(omega: float, time: float, hbar: float = 1.0) -> np.ndarray:
    return unitary_from_hamiltonian(coherent_z_hamiltonian(omega, hbar), time, hbar)
