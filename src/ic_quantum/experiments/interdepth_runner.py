"""Minimal experiment for a latent causal transformation between circuit depths.

Programmed circuit:
    |0> -- H -- C_A -- H -- measurement/analysis

C_A is evaluated in three controlled cases:
1. identity (ideal control);
2. a coherent unitary perturbation, directly reversible by U_A^dagger;
3. a dephasing CPTP channel, for which a single system-only unitary cannot
   generally restore a pure target once the state has become mixed.

The experiment validates the computational concept. It does not identify a real
physical causal agent and does not prove uniqueness of an agent signature.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ic_quantum.channels.dephasing import dephasing_kraus
from ic_quantum.channels.unitary import coherent_z_unitary
from ic_quantum.core.operators import HADAMARD
from ic_quantum.core.states import reference_density
from ic_quantum.data.interdepth_schema import InterdepthExperimentRecord
from ic_quantum.dynamics.causal_latent import (
    LatentCausalTransform,
    LatentTransformKind,
)
from ic_quantum.dynamics.closed_system import apply_unitary
from ic_quantum.dynamics.reversibility import (
    max_unitary_recovery_fidelity_to_pure_target,
)
from ic_quantum.metrics.coherence import l1_coherence
from ic_quantum.metrics.entropy import von_neumann_entropy
from ic_quantum.metrics.fidelity import fidelity
from ic_quantum.metrics.purity import purity

EXPERIMENT_ID = "fase2_exp02_latent_causal_interdepth"
DEFAULT_SEED = 20260918


def _build_transforms(
    omega: float,
    time: float,
    p_dephasing: float,
) -> list[tuple[str, LatentCausalTransform]]:
    return [
        (
            "control_identity",
            LatentCausalTransform(
                transform_id="C_identity_d1",
                depth_after=1,
                kind=LatentTransformKind.IDENTITY,
                dimension=2,
                agent_id=None,
            ),
        ),
        (
            "unitary_causal_agent",
            LatentCausalTransform(
                transform_id="C_coherent_z_d1",
                depth_after=1,
                kind=LatentTransformKind.UNITARY,
                dimension=2,
                agent_id="coherent_z",
                parameters={"omega": float(omega), "time": float(time)},
                unitary=coherent_z_unitary(omega=omega, time=time),
            ),
        ),
        (
            "nonunitary_causal_agent",
            LatentCausalTransform(
                transform_id="C_dephasing_d1",
                depth_after=1,
                kind=LatentTransformKind.KRAUS_CPTP,
                dimension=2,
                agent_id="dephasing",
                parameters={"p": float(p_dephasing)},
                kraus_operators=tuple(dephasing_kraus(p_dephasing)),
            ),
        ),
    ]


def run_interdepth_experiment(
    omega: float = 1.0,
    time: float = 0.7,
    p_dephasing: float = 0.35,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Execute H -> C_A -> H for identity, unitary and non-unitary C_A."""
    rho_initial = reference_density("0")
    rho_interval_target = apply_unitary(rho_initial, HADAMARD)
    rho_final_target = apply_unitary(rho_interval_target, HADAMARD)

    rows: list[dict] = []
    for case_id, latent in _build_transforms(omega, time, p_dephasing):
        rho_after_latent = latent.apply(rho_interval_target)
        rho_final_uncorrected = apply_unitary(rho_after_latent, HADAMARD)

        assessment = latent.reversibility_assessment()
        if assessment is None:
            raise RuntimeError("Controlled experiment requires an assessable latent map.")

        inverse = latent.direct_unitary_inverse()
        direct_recovery_applied = inverse is not None
        recovery_fidelity: float | None = None
        final_after_recovery: float | None = None

        if inverse is not None:
            rho_recovered_interval = apply_unitary(rho_after_latent, inverse)
            recovery_fidelity = fidelity(rho_interval_target, rho_recovered_interval)
            rho_final_recovered = apply_unitary(rho_recovered_interval, HADAMARD)
            final_after_recovery = fidelity(rho_final_target, rho_final_recovered)

        unitary_recovery_bound = max_unitary_recovery_fidelity_to_pure_target(
            rho_after_latent,
            rho_interval_target,
        )

        start, end = latent.interval
        rows.append(
            InterdepthExperimentRecord(
                experiment_id=EXPERIMENT_ID,
                case_id=case_id,
                transform_id=latent.transform_id,
                agent_id=latent.agent_id,
                agent_parameters=latent.parameters,
                initial_state="0",
                programmed_gate_1="H",
                programmed_gate_2="H",
                interval_start_depth=start,
                interval_end_depth=end,
                transform_kind=latent.kind.value,
                entropy_after_latent=von_neumann_entropy(rho_after_latent),
                purity_after_latent=purity(rho_after_latent),
                coherence_after_latent=l1_coherence(rho_after_latent),
                fidelity_to_interval_target=fidelity(
                    rho_interval_target, rho_after_latent
                ),
                direct_unitary_inverse_available=inverse is not None,
                direct_recovery_applied=direct_recovery_applied,
                recovery_fidelity_at_interval=recovery_fidelity,
                max_unitary_recovery_fidelity_bound=unitary_recovery_bound,
                final_fidelity_uncorrected=fidelity(
                    rho_final_target, rho_final_uncorrected
                ),
                final_fidelity_after_direct_recovery=final_after_recovery,
                reversibility_class=assessment.classification,
                linear_invertible=assessment.linear_invertible,
                inverse_cptp=assessment.inverse_cptp,
                direct_unitary_inverse=assessment.direct_unitary_inverse,
                random_seed=seed,
            ).to_dict()
        )

    return pd.DataFrame(rows)


def save_interdepth_results(
    output_dir: Path,
    omega: float = 1.0,
    time: float = 0.7,
    p_dephasing: float = 0.35,
    seed: int = DEFAULT_SEED,
) -> tuple[Path, Path]:
    """Save the experiment table and its explicit reproducibility configuration."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dataframe = run_interdepth_experiment(
        omega=omega,
        time=time,
        p_dephasing=p_dephasing,
        seed=seed,
    )

    csv_path = output_dir / "interdepth_latent_experiment.csv"
    dataframe_for_csv = dataframe.copy()
    dataframe_for_csv["agent_parameters"] = dataframe_for_csv["agent_parameters"].map(
        lambda value: json.dumps(value, sort_keys=True)
    )
    dataframe_for_csv.to_csv(csv_path, index=False)

    metadata = {
        "experiment_id": EXPERIMENT_ID,
        "initial_state": "0",
        "programmed_gates": ["H", "H"],
        "latent_interval": [1, 2],
        "omega": float(omega),
        "interaction_time": float(time),
        "p_dephasing": float(p_dephasing),
        "seed": int(seed),
        "scientific_scope": (
            "Controlled validation of latent inter-depth transformations; "
            "not physical-agent identification."
        ),
    }
    metadata_path = output_dir / "interdepth_latent_experiment_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return csv_path, metadata_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results", type=Path)
    parser.add_argument("--omega", default=1.0, type=float)
    parser.add_argument("--time", default=0.7, type=float)
    parser.add_argument("--p-dephasing", default=0.35, type=float)
    parser.add_argument("--seed", default=DEFAULT_SEED, type=int)
    args = parser.parse_args()

    csv_path, metadata_path = save_interdepth_results(
        output_dir=args.output_dir,
        omega=args.omega,
        time=args.time,
        p_dephasing=args.p_dephasing,
        seed=args.seed,
    )
    print(pd.read_csv(csv_path).to_string(index=False))
    print(f"\nSaved: {csv_path}")
    print(f"Saved: {metadata_path}")


if __name__ == "__main__":
    main()
