"""Quantized mechanical/phonon mode coupled to a two-level system.

The model is the resonant Jaynes-Cummings interaction used in circuit quantum
acoustodynamics, with a finite Fock-space truncation for the mechanical mode:

H/hbar = omega_q |1><1| + omega_m b^dagger b
         + g (sigma_+ b + sigma_- b^dagger).

The mechanical mode may start in a thermal state.  The reduced qubit dynamics is
obtained from the explicit global unitary followed by partial trace.
"""

from __future__ import annotations

import numpy as np
from scipy.constants import hbar, k
from scipy.linalg import expm

from ic_quantum.core.operators import I2, PROJECTOR_1
from ic_quantum.core.validation import validate_density_matrix, validate_kraus, validate_unitary
from ic_quantum.dynamics.partial_trace import partial_trace_bipartite


SIGMA_PLUS = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=complex)
SIGMA_MINUS = SIGMA_PLUS.conjugate().T


def annihilation_operator(dimension: int) -> np.ndarray:
    if dimension < 2:
        raise ValueError("mechanical_mode_dimension must be >= 2.")
    operator = np.zeros((dimension, dimension), dtype=complex)
    for n in range(1, dimension):
        operator[n - 1, n] = np.sqrt(float(n))
    return operator


def thermal_mean_occupation(
    mode_angular_frequency: float,
    temperature_kelvin: float,
) -> float:
    omega = float(mode_angular_frequency)
    temperature = float(temperature_kelvin)
    if omega <= 0:
        raise ValueError("mode_angular_frequency must be positive.")
    if temperature < 0:
        raise ValueError("temperature_kelvin must be non-negative.")
    if temperature == 0:
        return 0.0
    exponent = hbar * omega / (k * temperature)
    if exponent > 700:
        return 0.0
    return float(1.0 / np.expm1(exponent))


def thermal_truncation_tail_probability(
    mode_angular_frequency: float,
    temperature_kelvin: float,
    dimension: int,
) -> float:
    """Probability mass omitted above the finite Fock cutoff for a thermal mode."""
    if dimension < 1:
        raise ValueError("dimension must be positive.")
    nbar = thermal_mean_occupation(mode_angular_frequency, temperature_kelvin)
    if nbar == 0.0:
        return 0.0
    ratio = nbar / (nbar + 1.0)
    return float(ratio ** dimension)


def truncated_thermal_state(
    mode_angular_frequency: float,
    temperature_kelvin: float,
    dimension: int,
) -> np.ndarray:
    nbar = thermal_mean_occupation(mode_angular_frequency, temperature_kelvin)
    if nbar == 0.0:
        rho = np.zeros((dimension, dimension), dtype=complex)
        rho[0, 0] = 1.0
        return rho
    ratio = nbar / (nbar + 1.0)
    probabilities = ratio ** np.arange(dimension, dtype=float)
    probabilities /= probabilities.sum()
    rho = np.diag(probabilities.astype(complex))
    validate_density_matrix(rho)
    return rho


def mechanical_joint_angular_hamiltonian(
    *,
    mode_angular_frequency: float,
    coupling_rate: float,
    mode_dimension: int,
    qubit_angular_frequency: float | None = None,
) -> np.ndarray:
    """Return H/hbar in rad/s for a resonant or near-resonant qubit-mode model."""
    omega_m = float(mode_angular_frequency)
    omega_q = omega_m if qubit_angular_frequency is None else float(qubit_angular_frequency)
    g = float(coupling_rate)
    if omega_m <= 0 or omega_q <= 0:
        raise ValueError("Qubit and mechanical angular frequencies must be positive.")
    if g < 0:
        raise ValueError("coupling_rate must be non-negative.")

    b = annihilation_operator(mode_dimension)
    bdag = b.conjugate().T
    number = bdag @ b
    i_mode = np.eye(mode_dimension, dtype=complex)
    h_over_hbar = (
        omega_q * np.kron(PROJECTOR_1, i_mode)
        + omega_m * np.kron(I2, number)
        + g * (
            np.kron(SIGMA_PLUS, b)
            + np.kron(SIGMA_MINUS, bdag)
        )
    )
    if not np.allclose(h_over_hbar, h_over_hbar.conjugate().T, atol=1e-10, rtol=0.0):
        raise RuntimeError("Mechanical joint Hamiltonian is not Hermitian.")
    return h_over_hbar


def mechanical_joint_unitary(*, time: float, **kwargs: float) -> np.ndarray:
    t = float(time)
    if t < 0:
        raise ValueError("time must be non-negative.")
    h_over_hbar = mechanical_joint_angular_hamiltonian(**kwargs)
    unitary = expm(-1.0j * h_over_hbar * t)
    validate_unitary(unitary)
    return unitary


def reduced_mechanical_phonon_dynamics(
    rho_system: np.ndarray,
    *,
    mode_angular_frequency: float,
    coupling_rate: float,
    temperature_kelvin: float,
    mode_dimension: int,
    time: float,
    qubit_angular_frequency: float | None = None,
) -> np.ndarray:
    validate_density_matrix(rho_system)
    if rho_system.shape != (2, 2):
        raise ValueError("The mechanical-phonon model currently targets one qubit.")
    rho_mode = truncated_thermal_state(
        mode_angular_frequency, temperature_kelvin, mode_dimension
    )
    unitary = mechanical_joint_unitary(
        time=time,
        mode_angular_frequency=mode_angular_frequency,
        coupling_rate=coupling_rate,
        mode_dimension=mode_dimension,
        qubit_angular_frequency=qubit_angular_frequency,
    )
    joint = np.kron(rho_system, rho_mode)
    evolved = unitary @ joint @ unitary.conjugate().T
    return partial_trace_bipartite(
        evolved,
        dims=(2, mode_dimension),
        trace_out="B",
    )


def mechanical_phonon_kraus(
    *,
    mode_angular_frequency: float,
    coupling_rate: float,
    temperature_kelvin: float,
    mode_dimension: int,
    time: float,
    qubit_angular_frequency: float | None = None,
) -> list[np.ndarray]:
    """Construct Kraus operators from U and a diagonal truncated thermal state."""
    rho_mode = truncated_thermal_state(
        mode_angular_frequency, temperature_kelvin, mode_dimension
    )
    probabilities = np.real(np.diag(rho_mode))
    unitary = mechanical_joint_unitary(
        time=time,
        mode_angular_frequency=mode_angular_frequency,
        coupling_rate=coupling_rate,
        mode_dimension=mode_dimension,
        qubit_angular_frequency=qubit_angular_frequency,
    )
    tensor = unitary.reshape(2, mode_dimension, 2, mode_dimension)
    kraus: list[np.ndarray] = []
    for n, probability in enumerate(probabilities):
        if probability <= 1e-15:
            continue
        for m in range(mode_dimension):
            block = tensor[:, m, :, n]
            operator = np.sqrt(probability) * block
            if np.linalg.norm(operator) > 1e-14:
                kraus.append(operator)
    validate_kraus(kraus)
    return kraus
