"""First end-to-end experiment for the second stage of the IC.

This experiment validates infrastructure; it is not a test of the main Causal-Agent
hypothesis and does not train machine-learning models.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ic_quantum.agents.canonical import amplitude_damping_agent, coherent_z_agent, dephasing_agent
from ic_quantum.channels.amplitude_damping import amplitude_damping_dilation_unitary
from ic_quantum.core.states import REFERENCE_KETS, density_matrix
from ic_quantum.core.validation import validate_unitary
from ic_quantum.data.schema import ExperimentRecord
from ic_quantum.dynamics.closed_system import apply_unitary, unitary_from_hamiltonian
from ic_quantum.dynamics.open_system import apply_kraus
from ic_quantum.dynamics.partial_trace import partial_trace_bipartite
from ic_quantum.metrics.coherence import l1_coherence
from ic_quantum.metrics.entropy import von_neumann_entropy
from ic_quantum.metrics.fidelity import fidelity
from ic_quantum.metrics.purity import purity

DEFAULT_SEED = 20260916
EXPERIMENT_ID = "fase2_exp01_minimal_one_qubit"


def _metrics(rho_before: np.ndarray, rho_after: np.ndarray) -> dict[str, float]:
    return {
        "entropy_before": von_neumann_entropy(rho_before),
        "entropy_after": von_neumann_entropy(rho_after),
        "purity_before": purity(rho_before),
        "purity_after": purity(rho_after),
        "coherence_before": l1_coherence(rho_before),
        "coherence_after": l1_coherence(rho_after),
        "fidelity_to_ideal": fidelity(rho_before, rho_after),
    }


def run_first_experiment(omega: float = 1.0, time: float = 0.7, p_dephasing: float = 0.35, p_amplitude: float = 0.25, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Compare ideal, coherent unitary, dephasing and amplitude damping dynamics."""
    np.random.default_rng(seed)
    coherent = coherent_z_agent(omega)
    dephasing = dephasing_agent(p_dephasing)
    damping = amplitude_damping_agent(p_amplitude)
    coherent_u = unitary_from_hamiltonian(coherent.interaction_hamiltonian, time)
    validate_unitary(coherent_u)
    rows: list[dict] = []
    for state_name, ket in REFERENCE_KETS.items():
        rho = density_matrix(ket)
        for agent_id, parameters, channel_type, after, recovery, rev_class, event_time in [
            ("ideal", {}, "identity", rho, 1.0, "identity", time),
            (coherent.agent_id, coherent.parameters, "unitary", apply_unitary(rho, coherent_u), None, coherent.reversibility_class or "unclassified", time),
            (dephasing.agent_id, dephasing.parameters, "kraus_cptp", apply_kraus(rho, dephasing.kraus_operators or []), None, dephasing.reversibility_class or "unclassified", None),
            (damping.agent_id, damping.parameters, "kraus_cptp", apply_kraus(rho, damping.kraus_operators or []), None, damping.reversibility_class or "unclassified", None),
        ]:
            recovery_fidelity = recovery
            if agent_id == coherent.agent_id:
                recovered = apply_unitary(after, coherent_u.conjugate().T)
                recovery_fidelity = fidelity(rho, recovered)
            rows.append(ExperimentRecord(
                experiment_id=EXPERIMENT_ID, agent_id=agent_id, initial_state=state_name,
                agent_parameters=parameters, channel_type=channel_type, time=event_time,
                recovery_fidelity=recovery_fidelity, reversibility_class=rev_class,
                random_seed=seed, **_metrics(rho, after),
            ).to_dict())
    return pd.DataFrame(rows)


def validate_global_reduced_equivalence(p: float = 0.25) -> dict[str, float]:
    """Verify a global unitary dilation reproduces amplitude damping after tracing A."""
    rho_s = density_matrix(REFERENCE_KETS["+"])
    rho_a = density_matrix(REFERENCE_KETS["0"])
    rho_sa = np.kron(rho_s, rho_a)
    unitary_sa = amplitude_damping_dilation_unitary(p)
    validate_unitary(unitary_sa)
    rho_sa_after = apply_unitary(rho_sa, unitary_sa)
    rho_s_reduced = partial_trace_bipartite(rho_sa_after, dims=(2, 2), trace_out="B")
    damping = amplitude_damping_agent(p)
    rho_s_kraus = apply_kraus(rho_s, damping.kraus_operators or [])
    return {
        "p": float(p),
        "global_unitary_valid": 1.0,
        "max_abs_difference_reduced_vs_kraus": float(np.max(np.abs(rho_s_reduced - rho_s_kraus))),
        "reduced_purity": purity(rho_s_reduced),
        "reduced_entropy": von_neumann_entropy(rho_s_reduced),
    }


def save_results(output_dir: Path, **parameters: float | int) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataframe = run_first_experiment(**parameters)
    csv_path = output_dir / "first_experiment.csv"
    dataframe_for_csv = dataframe.copy()
    dataframe_for_csv["agent_parameters"] = dataframe_for_csv["agent_parameters"].map(lambda value: json.dumps(value, sort_keys=True))
    dataframe_for_csv.to_csv(csv_path, index=False)
    p_amplitude = float(parameters.get("p_amplitude", 0.25))
    equivalence_path = output_dir / "global_reduced_validation.json"
    equivalence_path.write_text(json.dumps(validate_global_reduced_equivalence(p_amplitude), indent=2, sort_keys=True), encoding="utf-8")
    return csv_path, equivalence_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results", type=Path)
    parser.add_argument("--omega", default=1.0, type=float)
    parser.add_argument("--time", default=0.7, type=float)
    parser.add_argument("--p-dephasing", default=0.35, type=float)
    parser.add_argument("--p-amplitude", default=0.25, type=float)
    parser.add_argument("--seed", default=DEFAULT_SEED, type=int)
    args = parser.parse_args()
    csv_path, equivalence_path = save_results(args.output_dir, omega=args.omega, time=args.time, p_dephasing=args.p_dephasing, p_amplitude=args.p_amplitude, seed=args.seed)
    print(pd.read_csv(csv_path).to_string(index=False))
    print(f"\nSaved: {csv_path}")
    print(f"Saved: {equivalence_path}")


if __name__ == "__main__":
    main()
