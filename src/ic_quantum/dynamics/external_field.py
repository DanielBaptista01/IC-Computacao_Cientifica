"""Semiclassical external electromagnetic/magnetic-field perturbation.

This module models the magnetic component of an external coherent field acting on an
effective spin-1/2 qubit through the Zeeman interaction.  For a fixed field
orientation the Hamiltonian at different times commutes with itself, so the propagator
is analytical and no time-discretization error is introduced.

H_int(t)/hbar = [gamma B0 cos(omega t + phi)/2] n . sigma.
"""

from __future__ import annotations

import numpy as np

from ic_quantum.core.operators import I2, SIGMA_X, SIGMA_Y, SIGMA_Z
from ic_quantum.core.validation import validate_unitary
from ic_quantum.dynamics.closed_system import apply_unitary


def field_axis(polar_angle: float, azimuth_angle: float) -> np.ndarray:
    theta = float(polar_angle)
    phi = float(azimuth_angle)
    if not 0.0 <= theta <= np.pi:
        raise ValueError("polar_angle must lie in [0, pi].")
    return np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ],
        dtype=float,
    )


def integrated_zeeman_angle(
    *,
    gyromagnetic_ratio: float,
    field_amplitude: float,
    drive_angular_frequency: float,
    phase: float,
    time: float,
) -> float:
    """Return the accumulated rotation angle int_0^t gamma B(s) ds."""
    gamma = float(gyromagnetic_ratio)
    b0 = float(field_amplitude)
    omega = float(drive_angular_frequency)
    t = float(time)
    if gamma < 0:
        raise ValueError("gyromagnetic_ratio must be non-negative.")
    if b0 < 0:
        raise ValueError("field_amplitude must be non-negative.")
    if omega < 0:
        raise ValueError("drive_angular_frequency must be non-negative.")
    if t < 0:
        raise ValueError("time must be non-negative.")

    if np.isclose(omega, 0.0, atol=1e-15):
        integral = t * np.cos(float(phase))
    else:
        integral = (
            np.sin(omega * t + float(phase)) - np.sin(float(phase))
        ) / omega
    return gamma * b0 * integral


def external_magnetic_field_unitary(
    *,
    gyromagnetic_ratio: float,
    field_amplitude: float,
    drive_angular_frequency: float,
    phase: float,
    polar_angle: float,
    azimuth_angle: float,
    time: float,
) -> np.ndarray:
    """Analytical propagator for a fixed-orientation sinusoidal magnetic field."""
    axis = field_axis(polar_angle, azimuth_angle)
    angle = integrated_zeeman_angle(
        gyromagnetic_ratio=gyromagnetic_ratio,
        field_amplitude=field_amplitude,
        drive_angular_frequency=drive_angular_frequency,
        phase=phase,
        time=time,
    )
    generator = axis[0] * SIGMA_X + axis[1] * SIGMA_Y + axis[2] * SIGMA_Z
    unitary = (
        np.cos(angle / 2.0) * I2
        - 1.0j * np.sin(angle / 2.0) * generator
    )
    validate_unitary(unitary)
    return unitary


def apply_external_magnetic_field(
    rho: np.ndarray,
    **kwargs: float,
) -> np.ndarray:
    return apply_unitary(rho, external_magnetic_field_unitary(**kwargs))


def gaussian_quasistatic_field_coherence_factor(
    *,
    gyromagnetic_ratio: float,
    field_standard_deviation: float,
    time: float,
) -> float:
    """Ensemble coherence for a zero-mean quasistatic Gaussian longitudinal field.

    If delta B is Gaussian with standard deviation sigma_B and the qubit frequency
    shift is gamma*delta B, averaging exp[-i gamma deltaB t] gives
    W(t)=exp[-(gamma sigma_B t)^2/2].
    """
    gamma = float(gyromagnetic_ratio)
    sigma_b = float(field_standard_deviation)
    t = float(time)
    if gamma < 0 or sigma_b < 0 or t < 0:
        raise ValueError(
            "gyromagnetic_ratio, field_standard_deviation and time must be non-negative."
        )
    return float(np.exp(-0.5 * (gamma * sigma_b * t) ** 2))


def gaussian_quasistatic_field_kraus(
    *,
    gyromagnetic_ratio: float,
    field_standard_deviation: float,
    time: float,
) -> list[np.ndarray]:
    """Equivalent dephasing Kraus representation of the Gaussian field ensemble."""
    q = gaussian_quasistatic_field_coherence_factor(
        gyromagnetic_ratio=gyromagnetic_ratio,
        field_standard_deviation=field_standard_deviation,
        time=time,
    )
    return [
        np.sqrt((1.0 + q) / 2.0) * I2,
        np.sqrt((1.0 - q) / 2.0) * SIGMA_Z,
    ]


def apply_gaussian_quasistatic_field(rho: np.ndarray, **kwargs: float) -> np.ndarray:
    from ic_quantum.dynamics.open_system import apply_kraus

    return apply_kraus(rho, gaussian_quasistatic_field_kraus(**kwargs))
