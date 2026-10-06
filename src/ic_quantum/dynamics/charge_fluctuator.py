"""Bistable charge fluctuator / random-telegraph-noise dephasing.

A localized bistable charge defect modulates the qubit splitting through
    H_noise(t)/hbar = [v xi(t)/2] sigma_z,
where xi(t)=+-1 is a symmetric two-state Markov process whose transition rate out
of each state is nu.  Ensemble averaging gives an exact coherence factor W(t).

The implementation uses the explicit solution of
    W'' + 2 nu W' + v^2 W = 0,
with W(0)=1 and W'(0)=0.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import I2, SIGMA_Z
from ic_quantum.core.validation import validate_kraus
from ic_quantum.dynamics.open_system import apply_kraus


def random_telegraph_coherence_factor(
    *,
    coupling_rate: float,
    switching_rate: float,
    time: float,
) -> float:
    v = float(coupling_rate)
    nu = float(switching_rate)
    t = float(time)
    if v < 0 or nu < 0 or t < 0:
        raise ValueError("coupling_rate, switching_rate and time must be non-negative.")
    if v == 0 or t == 0:
        return 1.0

    if np.isclose(nu, v, rtol=1e-12, atol=1e-15):
        value = np.exp(-nu * t) * (1.0 + nu * t)
    elif nu > v:
        delta = np.sqrt(nu * nu - v * v)
        value = np.exp(-nu * t) * (
            np.cosh(delta * t) + (nu / delta) * np.sinh(delta * t)
        )
    else:
        mu = np.sqrt(v * v - nu * nu)
        value = np.exp(-nu * t) * (
            np.cos(mu * t) + (nu / mu) * np.sin(mu * t)
        )
    # Exact dynamics obeys |W|<=1. Clamp only numerical overshoot.
    if abs(value) > 1.0 + 1e-10:
        raise RuntimeError("Random-telegraph coherence factor left the physical interval.")
    return float(np.clip(value, -1.0, 1.0))


def random_telegraph_spectral_density(
    angular_frequency: float,
    *,
    coupling_rate: float,
    switching_rate: float,
) -> float:
    """Two-sided PSD for v*xi(t), with <xi(t)xi(0)>=exp(-2 nu |t|)."""
    omega = float(angular_frequency)
    v = float(coupling_rate)
    nu = float(switching_rate)
    if v < 0 or nu < 0:
        raise ValueError("coupling_rate and switching_rate must be non-negative.")
    if nu == 0:
        return 0.0
    return float(4.0 * v * v * nu / (omega * omega + 4.0 * nu * nu))


def random_telegraph_dephasing_kraus(
    *,
    coupling_rate: float,
    switching_rate: float,
    time: float,
) -> list[np.ndarray]:
    w = random_telegraph_coherence_factor(
        coupling_rate=coupling_rate,
        switching_rate=switching_rate,
        time=time,
    )
    operators = [
        np.sqrt((1.0 + w) / 2.0) * I2,
        np.sqrt((1.0 - w) / 2.0) * SIGMA_Z,
    ]
    validate_kraus(operators)
    return operators


def apply_random_telegraph_charge_noise(rho: np.ndarray, **kwargs: float) -> np.ndarray:
    return apply_kraus(rho, random_telegraph_dephasing_kraus(**kwargs))
