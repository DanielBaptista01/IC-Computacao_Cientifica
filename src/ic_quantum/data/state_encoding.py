"""Lossless JSON-compatible encoding for complex matrices."""

from __future__ import annotations

from typing import Any

import numpy as np


def encode_complex_matrix(matrix: np.ndarray) -> dict[str, Any]:
    matrix = np.asarray(matrix, dtype=complex)
    if matrix.ndim != 2:
        raise ValueError("matrix must be two-dimensional.")
    return {
        "shape": [int(matrix.shape[0]), int(matrix.shape[1])],
        "real": matrix.real.tolist(),
        "imag": matrix.imag.tolist(),
    }


def decode_complex_matrix(payload: dict[str, Any]) -> np.ndarray:
    shape = tuple(int(v) for v in payload["shape"])
    real = np.asarray(payload["real"], dtype=float)
    imag = np.asarray(payload["imag"], dtype=float)
    if real.shape != shape or imag.shape != shape:
        raise ValueError("Encoded complex matrix shape is inconsistent.")
    return real + 1.0j * imag
