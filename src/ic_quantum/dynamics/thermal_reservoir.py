"""Finite-temperature Markovian photon-reservoir dynamics.

Master equation
    d rho/dt = gamma(nbar+1) D[sigma_-]rho
             + gamma nbar D[sigma_+]rho.

The exact qubit semigroup is generalized amplitude damping with equilibrium
ground population p_g=(nbar+1)/(2*nbar+1) and
lambda=1-exp[-gamma(2*nbar+1)t].
"""

from __future__ import annotations

import numpy as np
from scipy.constants import Boltzmann, hbar

from ic_quantum.core.validation import validate_kraus
from ic_quantum.dynamics.open_system import apply_kraus


def bose_occupation(
    transition_angular_frequency: float,
    temperature_kelvin: float,
) -> float:
    omega = float(transition_angular_frequency)
    temperature = float(temperature_kelvin)
    if omega <= 0:
        raise ValueError("transition_angular_frequency must be positive.")
    if temperature < 0:
        raise ValueError("temperature_kelvin must be non-negative.")
    if temperature == 0:
        return 0.0
    exponent = hbar * omega / (Boltzmann * temperature)
    if exponent > 700:
        return 0.0
    return float(1.0 / np.expm1(exponent))


def thermal_relaxation_parameter(
    decay_rate: float,
    nbar: float,
    time: float,
) -> float:
    gamma = float(decay_rate)
    occupation = float(nbar)
    t = float(time)
    if gamma < 0 or occupation < 0 or t < 0:
        raise ValueError("decay_rate, nbar and time must be non-negative.")
    return float(
        1.0 - np.exp(-gamma * (2.0 * occupation + 1.0) * t)
    )


def generalized_amplitude_damping_kraus(
    decay_rate: float,
    nbar: float,
    time: float,
) -> list[np.ndarray]:
    occupation = float(nbar)
    lam = thermal_relaxation_parameter(decay_rate, occupation, time)
    p_ground = (occupation + 1.0) / (2.0 * occupation + 1.0)
    s = np.sqrt(1.0 - lam)
    r = np.sqrt(lam)
    pg = np.sqrt(p_ground)
    pe = np.sqrt(1.0 - p_ground)
    operators = [
        pg * np.array([[1.0, 0.0], [0.0, s]], dtype=complex),
        pg * np.array([[0.0, r], [0.0, 0.0]], dtype=complex),
        pe * np.array([[s, 0.0], [0.0, 1.0]], dtype=complex),
        pe * np.array([[0.0, 0.0], [r, 0.0]], dtype=complex),
    ]
    validate_kraus(operators)
    return operators


def apply_thermal_photon_reservoir(
    rho: np.ndarray,
    *,
    decay_rate: float,
    transition_angular_frequency: float,
    temperature_kelvin: float,
    time: float,
) -> np.ndarray:
    nbar = bose_occupation(
        transition_angular_frequency, temperature_kelvin
    )
    return apply_kraus(
        rho,
        generalized_amplitude_damping_kraus(decay_rate, nbar, time),
    )
