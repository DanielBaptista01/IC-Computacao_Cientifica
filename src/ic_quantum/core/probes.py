"""Reference and final probe-state ensembles for one-qubit characterization."""

from __future__ import annotations

from itertools import product

import numpy as np

from ic_quantum.core.operators import I2, SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.states import KET_0, KET_1, density_matrix

KET_PLUS_I = (KET_0 + 1.0j * KET_1) / np.sqrt(2.0)
KET_MINUS_I = (KET_0 - 1.0j * KET_1) / np.sqrt(2.0)

STANDARD_PROBE_KETS = {
    "0": KET_0,
    "1": KET_1,
    "+": (KET_0 + KET_1) / np.sqrt(2.0),
    "-": (KET_0 - KET_1) / np.sqrt(2.0),
    "+i": KET_PLUS_I,
    "-i": KET_MINUS_I,
}


def standard_probe_densities() -> dict[str, np.ndarray]:
    return {name: density_matrix(ket) for name, ket in STANDARD_PROBE_KETS.items()}


def density_from_bloch(vector: tuple[float, float, float]) -> np.ndarray:
    """Return rho=(I+r.sigma)/2 for a physical one-qubit Bloch vector."""
    r = np.asarray(vector, dtype=float)
    if r.shape != (3,) or np.linalg.norm(r) > 1.0 + 1e-12:
        raise ValueError("Bloch vector must have shape (3,) and norm <= 1.")
    rho = 0.5 * (I2 + r[0] * SIGMA_X + r[1] * SIGMA_Y + r[2] * SIGMA_Z)
    return np.asarray(rho, dtype=complex)


def _cube_probe_densities() -> dict[str, np.ndarray]:
    """Eight symmetric pure states at the vertices of the Bloch-sphere cube."""
    result: dict[str, np.ndarray] = {}
    scale = 1.0 / np.sqrt(3.0)
    for signs in product((-1.0, 1.0), repeat=3):
        label = "cube_" + "".join("p" if sign > 0 else "m" for sign in signs)
        result[label] = density_from_bloch(tuple(scale * sign for sign in signs))
    return result


def final_probe_densities() -> dict[str, np.ndarray]:
    """Fourteen-state final ensemble: six Pauli-axis states plus eight cube vertices."""
    return {**standard_probe_densities(), **_cube_probe_densities()}


FINAL_PROBE_IDS: tuple[str, ...] = tuple(final_probe_densities().keys())
