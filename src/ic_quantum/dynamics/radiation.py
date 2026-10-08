"""Phenomenological ionizing-radiation / quasiparticle-burst model.

The physical chain represented here is:
ionizing event -> high-energy phonons -> broken Cooper pairs / quasiparticles
-> enhanced superconducting-qubit relaxation.

The quasiparticle fraction x obeys the literature kinetic model
    dx/dt = -r x^2 - s x + g,
and the qubit relaxation rate is
    Gamma_1(t) = C x(t) + Gamma_ex.
The resulting one-qubit map is amplitude damping with survival
    eta(t) = exp[- integral_0^t Gamma_1(s) ds].

This is intentionally a phenomenological reduced model: it does not invent a
microscopic Hamiltonian for the radiation event.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from ic_quantum.channels.amplitude_damping import amplitude_damping_kraus
from ic_quantum.dynamics.open_system import apply_kraus


def quasiparticle_fraction_and_hazard(
    *,
    initial_quasiparticle_fraction: float,
    recombination_rate: float,
    trapping_rate: float,
    generation_rate: float,
    qp_relaxation_coefficient: float,
    background_relaxation_rate: float,
    time: float,
) -> tuple[float, float]:
    x0 = float(initial_quasiparticle_fraction)
    r = float(recombination_rate)
    s = float(trapping_rate)
    g = float(generation_rate)
    c = float(qp_relaxation_coefficient)
    gamma_ex = float(background_relaxation_rate)
    t = float(time)
    if x0 < 0 or r < 0 or s < 0 or g < 0 or c < 0 or gamma_ex < 0 or t < 0:
        raise ValueError("Radiation/quasiparticle model parameters must be non-negative.")
    if t == 0:
        return x0, 0.0

    def rhs(_time: float, y: np.ndarray) -> tuple[float, float]:
        x = max(float(y[0]), 0.0)
        dx = -r * x * x - s * x + g
        dh = c * x + gamma_ex
        return dx, dh

    solution = solve_ivp(
        rhs,
        (0.0, t),
        (x0, 0.0),
        rtol=1e-10,
        atol=1e-13,
    )
    if not solution.success:
        raise RuntimeError("Quasiparticle kinetics integration failed.")
    x = float(solution.y[0, -1])
    hazard = float(solution.y[1, -1])
    if x < -1e-10 or hazard < -1e-10:
        raise RuntimeError("Quasiparticle kinetics produced an unphysical result.")
    return max(0.0, x), max(0.0, hazard)


def ionizing_radiation_relaxation_probability(**kwargs: float) -> float:
    _, hazard = quasiparticle_fraction_and_hazard(**kwargs)
    probability = 1.0 - np.exp(-hazard)
    return float(np.clip(probability, 0.0, 1.0))


def ionizing_radiation_kraus(**kwargs: float) -> list[np.ndarray]:
    return amplitude_damping_kraus(
        ionizing_radiation_relaxation_probability(**kwargs)
    )


def apply_ionizing_radiation_burst(rho: np.ndarray, **kwargs: float) -> np.ndarray:
    return apply_kraus(rho, ionizing_radiation_kraus(**kwargs))
