"""One-qubit depolarizing channel E(rho) = (1-p)rho + p I/2."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import I2, SIGMA_X, SIGMA_Y, SIGMA_Z


def depolarizing_kraus(p: float) -> list[np.ndarray]:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1].")
    return [
        np.sqrt(1.0 - 3.0 * p / 4.0) * I2,
        np.sqrt(p / 4.0) * SIGMA_X,
        np.sqrt(p / 4.0) * SIGMA_Y,
        np.sqrt(p / 4.0) * SIGMA_Z,
    ]
