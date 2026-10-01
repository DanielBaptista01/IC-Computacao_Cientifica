import json

import numpy as np

from ic_quantum.analysis.identifiability import summarize_identifiability
from ic_quantum.data.export import export_scientific_dataset
from ic_quantum.data.generator import (
    generate_coherent_detuning_samples,
    generate_exchange_relaxation_samples,
    generate_scaled_first_lot_samples,
)
from ic_quantum.data.scale_protocol import ScaledDatasetConfig
from ic_quantum.data.state_encoding import decode_complex_matrix
from ic_quantum.core.validation import validate_density_matrix


def test_scaled_protocol_generates_expected_nonduplicated_sample_count():
    config = ScaledDatasetConfig()
    samples = generate_scaled_first_lot_samples(config)
    assert len(samples) == 900
    assert len({sample.sample_id for sample in samples}) == 900
    assert len({sample.agent_model_id for sample in samples}) == 2


def test_every_scaled_sample_preserves_a_valid_simulated_density_matrix():
    samples = generate_scaled_first_lot_samples(ScaledDatasetConfig())
    for sample in samples[::37]:
        rho = decode_complex_matrix(
            sample.signature.extra["simulated_density_matrix"]
        )
        validate_density_matrix(rho)


def test_same_dimensionless_phase_can_be_nonidentifiable_within_one_model():
    coherent_a = generate_coherent_detuning_samples(
        detuning=1.0, times=(0.7,), probe_ids=("+i",)
    )[0]
    coherent_b = generate_coherent_detuning_samples(
        detuning=2.0, times=(0.35,), probe_ids=("+i",)
    )[0]
    rho_a = decode_complex_matrix(
        coherent_a.signature.extra["simulated_density_matrix"]
    )
    rho_b = decode_complex_matrix(
        coherent_b.signature.extra["simulated_density_matrix"]
    )
    assert np.allclose(rho_a, rho_b, atol=1e-10, rtol=0.0)

    exchange_a = generate_exchange_relaxation_samples(
        coupling=1.0, times=(0.7,), probe_ids=("+",)
    )[0]
    exchange_b = generate_exchange_relaxation_samples(
        coupling=2.0, times=(0.35,), probe_ids=("+",)
    )[0]
    rho_a = decode_complex_matrix(
        exchange_a.signature.extra["simulated_density_matrix"]
    )
    rho_b = decode_complex_matrix(
        exchange_b.signature.extra["simulated_density_matrix"]
    )
    assert np.allclose(rho_a, rho_b, atol=1e-10, rtol=0.0)


def test_identifiability_analysis_records_both_separation_and_nonidentifiability():
    config = ScaledDatasetConfig()
    samples = generate_scaled_first_lot_samples(config)
    summary = summarize_identifiability(
        samples,
        "coherent-longitudinal-detuning",
        "finite-two-level-exchange-relaxation",
        atol=config.identifiability_atol,
    )
    assert summary["matched_comparisons"] == 450
    assert 0 < summary["nonidentifiable_count"] < 450
    assert summary["per_probe"]["0"]["nonidentifiable_fraction"] == 1.0
    assert np.isclose(summary["per_probe"]["1"]["max_trace_distance"], 1.0)


def test_export_separates_observable_features_from_causal_labels(tmp_path):
    config = ScaledDatasetConfig(
        rate_values_rad_s=(1.0,),
        time_min_s=0.0,
        time_max_s=np.pi / 2,
        time_points=3,
        probe_ids=("0", "+i"),
    )
    samples = generate_scaled_first_lot_samples(config)
    paths = export_scientific_dataset(samples, config, tmp_path)

    feature_header = paths["features"].read_text(encoding="utf-8").splitlines()[0]
    label_header = paths["labels"].read_text(encoding="utf-8").splitlines()[0]
    assert "agent_model_id" not in feature_header
    assert "parameter" not in feature_header
    assert "agent_model_id" in label_header

    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    assert metadata["number_of_agent_families"] == 2
    assert metadata["number_of_samples"] == 12
    assert metadata["random_seed"] is None
