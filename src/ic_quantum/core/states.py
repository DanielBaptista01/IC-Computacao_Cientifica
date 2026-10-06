"""Reference qubit states and density-operator construction."""

from __future__ import annotations

import numpy as np

KET_0 = np.array([1.0, 0.0], dtype=complex)
KET_1 = np.array([0.0, 1.0], dtype=complex)
KET_PLUS = (KET_0 + KET_1) / np.sqrt(2.0)
KET_MINUS = (KET_0 - KET_1) / np.sqrt(2.0)

REFERENCE_KETS = {
    "0": KET_0,
    "1": KET_1,
    "+": KET_PLUS,
    "-": KET_MINUS,
}


def density_matrix(ket: np.ndarray) -> np.ndarray:
    """Return rho = |psi><psi| for a normalized state vector."""
    ket = np.asarray(ket, dtype=complex).reshape(-1)
    norm = np.linalg.norm(ket)
    if not np.isclose(norm, 1.0, atol=1e-12):
        raise ValueError(f"State vector must be normalized; got norm={norm}.")
    return np.outer(ket, ket.conjugate())


def reference_density(name: str) -> np.ndarray:
    """Return the density matrix of one of the reference states 0, 1, +, -."""
    try:
        return density_matrix(REFERENCE_KETS[name])
    except KeyError as exc:
        raise ValueError(f"Unknown reference state {name!r}.") from exc
