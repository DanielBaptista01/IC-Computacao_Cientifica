"""Pure dephasing channel with off-diagonal attenuation by (1-p)."""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import I2, PROJECTOR_0, PROJECTOR_1


def dephasing_kraus(p: float) -> list[np.ndarray]:
    """Return Kraus operators for E(rho)_01 = (1-p) rho_01.

    K0 = sqrt(1-p) I,
    K1 = sqrt(p) |0><0|,
    K2 = sqrt(p) |1><1|.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1].")
    return [
        np.sqrt(1.0 - p) * I2,
        np.sqrt(p) * PROJECTOR_0,
        np.sqrt(p) * PROJECTOR_1,
    ]
