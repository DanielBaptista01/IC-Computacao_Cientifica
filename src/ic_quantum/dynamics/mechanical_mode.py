"""Single-mode mechanical/phonon longitudinal pure-dephasing model.

For
    H_A/hbar = omega_m b^dagger b,
    H_int/hbar = g_m sigma_z (b+b^dagger),
and an initially thermal oscillator, the exact reduced coherence factor is

    q(t)=exp[-4(g_m/omega_m)^2 (1-cos(omega_m t))(2 nbar+1)].

This is a distinct coupling mechanism from the Jaynes-Cummings
excitation-exchange mechanical model in mechanical_phonon.py.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.spin_boson import spin_boson_dephasing_kraus


def mechanical_dephasing_exponent(
    time: float,
    mode_angular_frequency: float,
    coupling_rate: float,
    thermal_occupation: float,
) -> float:
    t = float(time)
    omega = float(mode_angular_frequency)
    coupling = float(coupling_rate)
    nbar = float(thermal_occupation)
    if t < 0 or omega <= 0 or coupling < 0 or nbar < 0:
        raise ValueError(
            "Require time>=0, omega>0, coupling>=0 and nbar>=0."
        )
    return float(
        4.0
        * (coupling / omega) ** 2
        * (1.0 - np.cos(omega * t))
        * (2.0 * nbar + 1.0)
    )


def mechanical_coherence_factor(
    time: float,
    mode_angular_frequency: float,
    coupling_rate: float,
    thermal_occupation: float,
) -> float:
    return float(
        np.exp(
            -mechanical_dephasing_exponent(
                time,
                mode_angular_frequency,
                coupling_rate,
                thermal_occupation,
            )
        )
    )


def apply_mechanical_mode_dephasing(
    rho: np.ndarray,
    *,
    time: float,
    mode_angular_frequency: float,
    coupling_rate: float,
    thermal_occupation: float,
) -> np.ndarray:
    q = mechanical_coherence_factor(
        time,
        mode_angular_frequency,
        coupling_rate,
        thermal_occupation,
    )
    return apply_kraus(rho, spin_boson_dephasing_kraus(q))
