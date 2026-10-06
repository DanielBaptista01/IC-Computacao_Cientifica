"""Basis-dependent l1 coherence."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.validation import validate_density_matrix


def l1_coherence(rho: np.ndarray) -> float:
    """C_l1(rho) = sum_{i != j} |rho_ij| in the computational basis."""
    validate_density_matrix(rho)
    off_diagonal = rho - np.diag(np.diag(rho))
    return float(np.sum(np.abs(off_diagonal)))
