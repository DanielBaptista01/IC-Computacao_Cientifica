import json

import numpy as np
import pandas as pd

from ic_quantum.experiments.interdepth_runner import (
    EXPERIMENT_ID,
    run_interdepth_experiment,
    save_interdepth_results,
)


def _row(frame, case_id):
    return frame.loc[frame["case_id"] == case_id].iloc[0]


def test_interdepth_experiment_distinguishes_three_controlled_cases():
    frame = run_interdepth_experiment(
        omega=1.0,
        time=0.7,
        p_dephasing=0.35,
        seed=20260918,
    )

    assert len(frame) == 3
    assert set(frame["case_id"]) == {
        "control_identity",
        "unitary_causal_agent",
        "nonunitary_causal_agent",
    }
    assert set(frame["experiment_id"]) == {EXPERIMENT_ID}

    control = _row(frame, "control_identity")
    assert np.isclose(control["fidelity_to_interval_target"], 1.0, atol=1e-10)
    assert np.isclose(control["final_fidelity_uncorrected"], 1.0, atol=1e-10)
    assert control["direct_unitary_inverse_available"]

    unitary = _row(frame, "unitary_causal_agent")
    assert np.isclose(unitary["purity_after_latent"], 1.0, atol=1e-10)
    assert np.isclose(unitary["entropy_after_latent"], 0.0, atol=1e-10)
    assert unitary["fidelity_to_interval_target"] < 1.0
    assert unitary["direct_unitary_inverse_available"]
    assert np.isclose(unitary["recovery_fidelity_at_interval"], 1.0, atol=1e-10)
    assert np.isclose(
        unitary["final_fidelity_after_direct_recovery"], 1.0, atol=1e-10
    )
    assert np.isclose(
        unitary["max_unitary_recovery_fidelity_bound"], 1.0, atol=1e-10
    )

    nonunitary = _row(frame, "nonunitary_causal_agent")
    assert np.isclose(nonunitary["purity_after_latent"], 0.71125, atol=1e-10)
    assert np.isclose(nonunitary["coherence_after_latent"], 0.65, atol=1e-10)
    assert np.isclose(nonunitary["fidelity_to_interval_target"], 0.825, atol=1e-10)
    assert not nonunitary["direct_unitary_inverse_available"]
    assert pd.isna(nonunitary["recovery_fidelity_at_interval"])
    assert pd.isna(nonunitary["final_fidelity_after_direct_recovery"])
    assert np.isclose(
        nonunitary["max_unitary_recovery_fidelity_bound"], 0.825, atol=1e-10
    )
    assert nonunitary["max_unitary_recovery_fidelity_bound"] < 1.0
    assert (
        nonunitary["reversibility_class"]
        == "class_II_linearly_invertible_without_CPTP_inverse"
    )


def test_interdepth_experiment_saves_reproducibility_metadata(tmp_path):
    csv_path, metadata_path = save_interdepth_results(
        tmp_path,
        omega=1.0,
        time=0.7,
        p_dephasing=0.35,
        seed=12345,
    )

    assert csv_path.exists()
    assert metadata_path.exists()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["experiment_id"] == EXPERIMENT_ID
    assert metadata["initial_state"] == "0"
    assert metadata["programmed_gates"] == ["H", "H"]
    assert metadata["latent_interval"] == [1, 2]
    assert metadata["seed"] == 12345
