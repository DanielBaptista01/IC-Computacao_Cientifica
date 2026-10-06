import json

import numpy as np
import pandas as pd

from ic_quantum.analysis.channel_collisions import exact_amplitude_damping_source_collision_table
from ic_quantum.analysis.final_identifiability import analyze_pairwise_identifiability
from ic_quantum.analysis.triad import analyze_agent_noise_entropy
from ic_quantum.data.final_export import export_final_dataset
from ic_quantum.data.final_generator import generate_final_dataset_samples
from ic_quantum.data.final_protocol import FinalDatasetConfig


def small_config():
    return FinalDatasetConfig(
        time_min_s=0.0,
        time_max_s=np.pi,
        time_points=5,
        probe_ids=("0", "1", "+", "cube_ppp"),
        coherent_detuning_rates=(0.5, 1.0),
        finite_exchange_couplings=(0.5, 1.0),
        photon_decay_rates=(0.2, 0.5),
        spin_boson_mode_counts=(2, 4),
        spin_boson_cutoffs=(1.0,),
        spin_boson_temperature_ratios=(1.0,),
    )


def test_final_export_separates_features_labels_and_provenance(tmp_path):
    config = small_config()
    samples = generate_final_dataset_samples(config)
    paths = export_final_dataset(samples, config, tmp_path)
    features = pd.read_csv(paths["observable_features_csv"])
    labels = pd.read_csv(paths["causal_labels_csv"])
    scientific = pd.read_parquet(paths["scientific_records_parquet"])

    assert "agent_model_id" not in features.columns
    assert "sample_id" not in features.columns
    assert "parameter_values_json" not in features.columns
    assert "agent_model_id" in labels.columns
    assert "density_matrix_json" in scientific.columns
    assert paths["observable_features_parquet"].exists()
    assert paths["provenance"].exists()

    metadata = json.loads(paths["metadata"].read_text())
    assert metadata["number_of_agent_families"] == 4
    assert metadata["rejected_samples"] == 0


def test_n_agent_identifiability_produces_all_six_agent_pairs():
    config = small_config()
    samples = generate_final_dataset_samples(config)
    result = analyze_pairwise_identifiability(samples, atol=config.identifiability_atol)
    assert len(result["pair_summary"]) == 6
    assert result["mean_min_distance_matrix"].shape == (4, 4)
    assert len(result["collision_regions"]) > 0


def test_all_agents_are_identical_at_zero_time_for_same_probe():
    config = small_config()
    samples = generate_final_dataset_samples(config)
    result = analyze_pairwise_identifiability(samples, atol=config.identifiability_atol)
    zero = result["condition_pairwise"][
        np.isclose(result["condition_pairwise"]["time_s"], 0.0)
    ]
    assert len(zero) == 6 * len(config.probe_ids)
    assert np.all(zero["min_trace_distance"] <= config.identifiability_atol)


def test_controlled_distinct_source_models_can_have_exact_same_reduced_channel():
    table = exact_amplitude_damping_source_collision_table()
    assert len(table) == 5
    assert table["max_trace_distance_across_probes"].max() < 1e-10


def test_unitary_causal_family_has_perturbations_without_entropy_change():
    config = small_config()
    samples = generate_final_dataset_samples(config)
    _, summary = analyze_agent_noise_entropy(samples)
    coherent = summary[
        summary["agent_model_id"] == "coherent-longitudinal-detuning"
    ].iloc[0]
    assert coherent["max_abs_delta_entropy"] < 1e-9
    assert coherent["max_trace_distance_to_input"] > 0.1
    assert coherent["perturbed_with_entropy_unchanged"] > 0
