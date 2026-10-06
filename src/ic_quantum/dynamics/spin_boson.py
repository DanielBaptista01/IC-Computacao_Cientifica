"""Finite-mode spin-boson pure-dephasing dynamics.

The implemented model follows the exactly solvable longitudinal spin-boson
interaction used in the project literature:

    H_int = sigma_z sum_k lambda_k (b_k + b_k^dagger)

For a thermal bath the reduced coherences are attenuated by exp[-Lambda(t)],
with Lambda(t) evaluated explicitly for a finite set of bosonic modes.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import I2, SIGMA_Z
from ic_quantum.core.validation import validate_density_matrix
from ic_quantum.dynamics.open_system import apply_kraus


def finite_mode_frequencies(mode_count: int, cutoff_angular_frequency: float) -> np.ndarray:
    if mode_count <= 0:
        raise ValueError("mode_count must be a positive integer.")
    cutoff = float(cutoff_angular_frequency)
    if cutoff <= 0:
        raise ValueError("cutoff_angular_frequency must be positive.")
    indices = np.arange(1, mode_count + 1, dtype=float)
    return indices * cutoff / float(mode_count)


def finite_mode_couplings(
    mode_count: int,
    cutoff_angular_frequency: float,
) -> np.ndarray:
    """Landi finite-mode Ohmic discretization: lambda_k = sqrt(Omega_k / N).

    Natural units are used for this controlled theoretical model: hbar = k_B = 1.
    """
    frequencies = finite_mode_frequencies(mode_count, cutoff_angular_frequency)
    return np.sqrt(frequencies / float(mode_count))


def _thermal_coth(frequency: np.ndarray, temperature_angular_frequency: float) -> np.ndarray:
    temperature = float(temperature_angular_frequency)
    if temperature < 0:
        raise ValueError("temperature_angular_frequency must be non-negative.")
    if temperature == 0:
        return np.ones_like(frequency, dtype=float)
    x = frequency / (2.0 * temperature)
    return 1.0 / np.tanh(x)


def finite_mode_dephasing_exponent(
    time: float,
    mode_count: int,
    cutoff_angular_frequency: float,
    temperature_angular_frequency: float,
) -> float:
    """Return the exact finite-mode decoherence exponent Lambda(t).

    Lambda(t) =
        sum_k 4 lambda_k^2 / Omega_k^2
        * [1-cos(Omega_k t)]
        * coth[Omega_k/(2T)].

    The formula is evaluated in natural units hbar = k_B = 1.
    """
    t = float(time)
    if t < 0:
        raise ValueError("time must be non-negative.")
    frequencies = finite_mode_frequencies(mode_count, cutoff_angular_frequency)
    couplings = finite_mode_couplings(mode_count, cutoff_angular_frequency)
    thermal = _thermal_coth(frequencies, temperature_angular_frequency)
    terms = (
        4.0
        * couplings**2
        / frequencies**2
        * (1.0 - np.cos(frequencies * t))
        * thermal
    )
    value = float(np.sum(terms))
    # The analytical expression is non-negative. Clamp tiny cancellation error only.
    if value < -1e-12:
        raise RuntimeError("Finite-mode dephasing exponent became physically negative.")
    return max(0.0, value)


def finite_mode_coherence_factor(
    time: float,
    mode_count: int,
    cutoff_angular_frequency: float,
    temperature_angular_frequency: float,
) -> float:
    exponent = finite_mode_dephasing_exponent(
        time=time,
        mode_count=mode_count,
        cutoff_angular_frequency=cutoff_angular_frequency,
        temperature_angular_frequency=temperature_angular_frequency,
    )
    return float(np.exp(-exponent))


def spin_boson_dephasing_kraus(coherence_factor: float) -> list[np.ndarray]:
    """Kraus form of rho_01 -> q rho_01 for 0 <= q <= 1."""
    q = float(coherence_factor)
    if not 0.0 <= q <= 1.0 + 1e-12:
        raise ValueError("coherence_factor must lie in [0, 1].")
    q = float(np.clip(q, 0.0, 1.0))
    return [
        np.sqrt((1.0 + q) / 2.0) * I2,
        np.sqrt((1.0 - q) / 2.0) * SIGMA_Z,
    ]


def apply_finite_mode_spin_boson_dephasing(
    rho: np.ndarray,
    *,
    time: float,
    mode_count: int,
    cutoff_angular_frequency: float,
    temperature_angular_frequency: float,
) -> np.ndarray:
    q = finite_mode_coherence_factor(
        time=time,
        mode_count=mode_count,
        cutoff_angular_frequency=cutoff_angular_frequency,
        temperature_angular_frequency=temperature_angular_frequency,
    )
    return apply_kraus(rho, spin_boson_dephasing_kraus(q))


def analytical_dephasing_map(rho: np.ndarray, coherence_factor: float) -> np.ndarray:
    """Direct analytical map used as an independent validation oracle."""
    rho = np.asarray(rho, dtype=complex)
    validate_density_matrix(rho)
    if rho.shape != (2, 2):
        raise ValueError("The spin-boson implementation currently targets one qubit.")
    q = float(coherence_factor)
    if not 0.0 <= q <= 1.0 + 1e-12:
        raise ValueError("coherence_factor must lie in [0, 1].")
    output = rho.copy()
    output[0, 1] *= q
    output[1, 0] *= q
    validate_density_matrix(output)
    return output
