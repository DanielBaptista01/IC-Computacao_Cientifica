"""Physical-response summaries for thermal and dephasing source families."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd


def _first_crossing(times: np.ndarray, values: np.ndarray, threshold: float) -> float:
    indices = np.flatnonzero(values <= threshold)
    if len(indices) == 0:
        return float("nan")
    return float(times[int(indices[0])])


def summarize_thermal_characteristic_times(samples) -> pd.DataFrame:
    """Estimate first-passage T1/T2-like scales without assuming exponential decay.

    T1* is the first sampled time at which the |1> population falls to <=1/e.
    T2* is the first sampled time at which transverse Bloch magnitude for |+>
    falls to <=1/e.  A missing crossing is reported as NaN, not infinity.
    For recurrent dynamics these are first-passage descriptors, not fitted constants.
    """
    thermal_agents = {
        "finite-mode-spin-boson-dephasing",
        "mechanical-phonon-mode",
    }
    rows = []
    for agent in sorted(thermal_agents):
        agent_samples = [s for s in samples if s.agent_model_id == agent]
        points = sorted({s.metadata["parameter_point_id"] for s in agent_samples})
        for point in points:
            excited = sorted(
                [
                    s for s in agent_samples
                    if s.metadata["parameter_point_id"] == point
                    and s.initial_system_state == "1"
                ],
                key=lambda s: float(s.time),
            )
            plus = sorted(
                [
                    s for s in agent_samples
                    if s.metadata["parameter_point_id"] == point
                    and s.initial_system_state == "+"
                ],
                key=lambda s: float(s.time),
            )
            if not excited or not plus:
                continue
            t1_times = np.asarray([float(s.time) for s in excited])
            p1 = np.asarray(
                [
                    (1.0 - float(s.signature.observables["Z"])) / 2.0
                    for s in excited
                ]
            )
            t2_times = np.asarray([float(s.time) for s in plus])
            transverse = np.asarray(
                [
                    np.hypot(
                        s.signature.observables["X"],
                        s.signature.observables["Y"],
                    )
                    for s in plus
                ]
            )
            entropy = np.asarray(
                [
                    s.signature.informational_metrics["entropy_after"]
                    for s in plus
                ]
            )
            purity = np.asarray(
                [
                    s.signature.informational_metrics["purity_after"]
                    for s in plus
                ]
            )
            fidelity = np.asarray(
                [
                    s.signature.informational_metrics["fidelity_to_input"]
                    for s in plus
                ]
            )
            parameters = plus[0].parameter_values
            rows.append(
                {
                    "agent_model_id": agent,
                    "parameter_point_id": point,
                    "physical_parameters_json": json.dumps(
                        parameters, sort_keys=True
                    ),
                    "t1_first_1_over_e_crossing_s": _first_crossing(
                        t1_times, p1, 1.0 / np.e
                    ),
                    "t2_first_1_over_e_crossing_s": _first_crossing(
                        t2_times, transverse, 1.0 / np.e
                    ),
                    "minimum_excited_population": float(np.min(p1)),
                    "minimum_transverse_bloch": float(np.min(transverse)),
                    "maximum_entropy_plus_probe": float(np.max(entropy)),
                    "minimum_purity_plus_probe": float(np.min(purity)),
                    "minimum_fidelity_plus_probe": float(np.min(fidelity)),
                }
            )
    return pd.DataFrame(rows)


def summarize_dephasing_trajectory_shapes(frame: pd.DataFrame) -> pd.DataFrame:
    """Quantify monotonicity, sign changes and revivals of representative dephasing."""
    rows = []
    for (agent, point), group in frame.groupby(
        ["agent_model_id", "parameter_point_id"]
    ):
        ordered = group.sort_values("normalized_time")
        x = ordered["x_coherence_response"].to_numpy(dtype=float)
        magnitude = np.abs(x)
        delta = np.diff(magnitude)
        sign = np.sign(x)
        sign_changes = int(
            np.sum((sign[1:] * sign[:-1]) < 0)
        )
        revival_steps = int(np.sum(delta > 1e-8))
        rows.append(
            {
                "agent_model_id": agent,
                "parameter_point_id": point,
                "minimum_abs_x_coherence": float(np.min(magnitude)),
                "final_x_coherence": float(x[-1]),
                "monotonic_nonincreasing_abs_coherence": bool(
                    np.all(delta <= 1e-8)
                ),
                "positive_revival_steps": revival_steps,
                "coherence_sign_changes": sign_changes,
            }
        )
    return pd.DataFrame(rows)
