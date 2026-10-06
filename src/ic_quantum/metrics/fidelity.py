"""Uhlmann state fidelity."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def _psd_sqrt(matrix: np.ndarray) -> np.ndarray:
    matrix = 0.5 * (matrix + matrix.conjugate().T)
    values, vectors = np.linalg.eigh(matrix)
    values = np.clip(values.real, 0.0, None)
    return (vectors * np.sqrt(values)) @ vectors.conjugate().T


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """F(rho,sigma) = [Tr sqrt(sqrt(rho) sigma sqrt(rho))]^2."""
    validate_density_matrix(rho)
    validate_density_matrix(sigma)
    root_rho = _psd_sqrt(rho)
    middle = root_rho @ sigma @ root_rho
    root_middle = _psd_sqrt(middle)
    value = float(np.real(np.trace(root_middle)) ** 2)
    return float(np.clip(value, 0.0, 1.0))
