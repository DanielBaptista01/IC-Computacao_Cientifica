"""Designed channel-collision experiment for distinct physical source models."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ic_quantum.core.probes import final_probe_densities
from ic_quantum.dynamics.markovian_reservoir import (
    apply_markovian_photon_reservoir_decay,
)
from ic_quantum.dynamics.microscopic import reduced_exchange_dynamics
from ic_quantum.metrics.distance import trace_distance


def exact_amplitude_damping_source_collision_table(
    probabilities: tuple[float, ...] = (0.1, 0.25, 0.5, 0.75, 0.9),
    observation_time: float = 1.0,
) -> pd.DataFrame:
    """Match p=sin^2(g t)=1-exp(-gamma t) for two distinct source models."""
    t = float(observation_time)
    if t <= 0:
        raise ValueError("observation_time must be positive.")
    rows = []
    probes = final_probe_densities()
    for p in probabilities:
        if not 0.0 < p < 1.0:
            raise ValueError("probabilities must lie strictly inside (0,1).")
        coupling = float(np.arcsin(np.sqrt(p)) / t)
        decay_rate = float(-np.log(1.0 - p) / t)
        distances = []
        for rho in probes.values():
            finite = reduced_exchange_dynamics(rho, coupling=coupling, time=t)
            markov = apply_markovian_photon_reservoir_decay(
                rho, decay_rate=decay_rate, time=t
            )
            distances.append(trace_distance(finite, markov))
        rows.append(
            {
                "target_damping_probability": p,
                "observation_time_s": t,
                "finite_exchange_coupling_rad_s": coupling,
                "markovian_decay_rate_s_inverse": decay_rate,
                "probe_count": len(probes),
                "max_trace_distance_across_probes": float(np.max(distances)),
                "mean_trace_distance_across_probes": float(np.mean(distances)),
            }
        )
    return pd.DataFrame(rows)
