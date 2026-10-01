"""Standardized probe states for causal-agent characterization.

The six states sample the positive/negative X, Y and Z Bloch axes. They are kept
separate from REFERENCE_KETS so legacy controlled experiments retain their
original four-state design.
"""

from __future__ import annotations

import numpy as np

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
