"""Basic one-qubit operators used explicitly in the mathematical models."""

import numpy as np

I2 = np.eye(2, dtype=complex)
SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
HADAMARD = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)

PROJECTOR_0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
PROJECTOR_1 = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
