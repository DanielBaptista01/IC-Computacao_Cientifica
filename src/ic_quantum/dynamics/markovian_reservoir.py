"""Markovian radiative relaxation of a two-level system.

The family represents a two-level system coupled to a photon reservoir under the
zero-temperature, undriven, weak-coupling Markovian limit. The reduced excited-state
population decays exponentially, so the effective amplitude-damping probability is

    p(t) = 1 - exp(-gamma t).

The channel is a reduced consequence of the source model and is not used as the
causal identity.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.dynamics.open_system import apply_kraus


def markovian_decay_probability(decay_rate: float, time: float) -> float:
    gamma = float(decay_rate)
    t = float(time)
    if gamma < 0:
        raise ValueError("decay_rate must be non-negative.")
    if t < 0:
        raise ValueError("time must be non-negative.")
    return float(1.0 - np.exp(-gamma * t))


def apply_markovian_photon_reservoir_decay(
    rho: np.ndarray,
    *,
    decay_rate: float,
    time: float,
) -> np.ndarray:
    p = markovian_decay_probability(decay_rate, time)
    return apply_kraus(rho, amplitude_damping_kraus(p))
