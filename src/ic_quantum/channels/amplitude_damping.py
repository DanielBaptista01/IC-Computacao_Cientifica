"""One-qubit amplitude damping and an explicit two-qubit unitary dilation."""

from __future__ import annotations

import numpy as np


def amplitude_damping_kraus(p: float) -> list[np.ndarray]:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1].")
    k0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - p)]], dtype=complex)
    k1 = np.array([[0.0, np.sqrt(p)], [0.0, 0.0]], dtype=complex)
    return [k0, k1]


def amplitude_damping_dilation_unitary(p: float) -> np.ndarray:
    """A 4x4 unitary on S+A reproducing amplitude damping for A initialized in |0>.

    Basis order: |00>, |01>, |10>, |11>, with system first and ancilla second.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1].")
    c = np.sqrt(1.0 - p)
    s = np.sqrt(p)
    return np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, s, 0.0],
            [0.0, -s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=complex,
    )
