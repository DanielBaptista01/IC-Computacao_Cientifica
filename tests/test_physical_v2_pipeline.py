import json

import numpy as np
import pandas as pd

from ic_quantum.analysis.physical_v2_identifiability import (
    analyze_physical_signature_overlap,
)
from ic_quantum.core.validation import validate_density_matrix
from ic_quantum.data.physical_v2_export import export_physical_v2_dataset
from ic_quantum.data.physical_v2_generator import generate_physical_v2_samples
from ic_quantum.data.physical_v2_protocol import PhysicalV2Config
from ic_quantum.data.state_encoding import decode_complex_matrix
from ic_quantum.analysis.physical_v2_response import (
    summarize_thermal_characteristic_times,
)
from ic_quantum.dynamics.mechanical_phonon import thermal_truncation_tail_probability


def small_config():
    return PhysicalV2Config(
        probe_ids=("0", "+"),
        em_field_amplitudes_t=(1e-7,),
        em_drive_frequencies_hz=(0.0,),
        em_orientations=("z",),
        em_gaussian_sigma_b_t=(1e-7,),
        em_time_points=3,
        thermal_mode_counts=(4,),
        thermal_cutoffs_rad_s=(1.0,),
        thermal_temperature_ratios=(0.5,),
        thermal_time_points=3,
        photon_decay_rates_s=(1e4,),
        photon_time_points=3,
        mechanical_frequencies_hz=(1e9,),
        mechanical_couplings_hz=(1e6,),
        mechanical_temperatures_k=(0.0,),
        mechanical_mode_dimension=4,
        mechanical_time_points=3,
        radiation_initial_xqp=(1e-5,),
        radiation_trapping_rates_s=(1e3,),
        radiation_time_points=3,
        charge_couplings_hz=(1e4,),
        charge_switching_rates_s=(1e4,),
        charge_time_points=3,
    )


def test_default_physical_v2_count_is_scientifically_scaled():
    assert PhysicalV2Config().expected_sample_count == 31570


def test_small_generator_covers_six_sources_with_valid_density_matrices():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    assert len(samples) == config.expected_sample_count
    assert len({s.agent_model_id for s in samples}) == 6
    assert len({s.sample_id for s in samples}) == len(samples)
    for sample in samples:
        rho = decode_complex_matrix(
            sample.signature.extra["simulated_density_matrix"]
        )
        validate_density_matrix(rho)
        assert sample.signature.physical_parameters
        assert "reversibility_class" in sample.signature.channel_descriptors


def test_export_separates_physical_source_labels_from_features(tmp_path):
    config = small_config()
    samples = generate_physical_v2_samples(config)
    paths = export_physical_v2_dataset(samples, config, tmp_path)
    features = pd.read_csv(paths["observable_features_csv"])
    labels = pd.read_csv(paths["causal_labels_csv"])
    scientific = pd.read_parquet(paths["scientific_records_parquet"])
    assert "physical_source" not in features.columns
    assert "causal_mechanism" not in features.columns
    assert "agent_model_id" not in features.columns
    assert "physical_source" in labels.columns
    assert "causal_mechanism" in labels.columns
    assert "physical_source" in scientific.columns
    metadata = json.loads(paths["metadata"].read_text())
    assert metadata["number_of_agent_families"] == 6
    assert (
        metadata["baseline_dataset"]["dataset_id"]
        == "ic_causal_agents_final_v1"
    )


def test_n_source_overlap_analysis_returns_all_fifteen_pairs():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    result = analyze_physical_signature_overlap(
        samples, atol=config.identifiability_atol
    )
    assert len(result["physical_pair_summary"]) == 15
    assert result["physical_mean_nearest_distance_matrix"].shape == (6, 6)


def test_all_physical_sources_collide_at_zero_time_for_same_probe():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    plus_zero = [
        s
        for s in samples
        if s.initial_system_state == "+" and np.isclose(s.time, 0.0)
    ]
    by_agent = {}
    for sample in plus_zero:
        by_agent.setdefault(sample.agent_model_id, sample)
    states = [
        decode_complex_matrix(
            sample.signature.extra["simulated_density_matrix"]
        )
        for sample in by_agent.values()
    ]
    assert len(states) == 6
    for rho in states[1:]:
        assert np.allclose(rho, states[0], atol=1e-9, rtol=0.0)


def test_external_field_has_coherent_and_ensemble_dephasing_regimes():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    em = [
        s
        for s in samples
        if s.agent_model_id == "external-magnetic-field-wave"
    ]
    regimes = {s.metadata["physical_regime"] for s in em}
    assert regimes == {
        "coherent_external_field",
        "stochastic_longitudinal_field",
    }
    coherent = [
        s
        for s in em
        if s.metadata["physical_regime"] == "coherent_external_field"
    ]
    assert (
        max(
            abs(s.signature.informational_metrics["delta_entropy"])
            for s in coherent
        )
        < 1e-9
    )


def test_observable_feature_payload_removes_physical_parameters_and_simulator_extras():
    config = small_config()
    sample = generate_physical_v2_samples(config)[0]
    payload = sample.observable_feature_payload()
    assert "physical_parameters" not in payload["signature"]
    assert "extra" not in payload["signature"]


def test_scientific_export_preserves_source_specific_signature_descriptors(tmp_path):
    config = small_config()
    samples = generate_physical_v2_samples(config)
    paths = export_physical_v2_dataset(samples, config, tmp_path)
    scientific = pd.read_csv(paths["scientific_records_csv"])
    assert "signature_extra_json" in scientific.columns
    charge = scientific[
        scientific["agent_model_id"] == "bistable-charge-fluctuator-rtn"
    ]
    assert charge["signature_extra_json"].str.contains("rtn_psd_at_2nu").any()


def test_default_mechanical_fock_truncation_omits_less_than_one_per_mille():
    config = PhysicalV2Config()
    tails = []
    for frequency_hz in config.mechanical_frequencies_hz:
        for temperature in config.mechanical_temperatures_k:
            tails.append(
                thermal_truncation_tail_probability(
                    2.0 * np.pi * frequency_hz,
                    temperature,
                    config.mechanical_mode_dimension,
                )
            )
    assert max(tails) < 1e-3


def test_spin_boson_thermal_model_has_no_t1_decay_in_its_validity_domain():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    summary = summarize_thermal_characteristic_times(samples)
    spin = summary[
        summary["agent_model_id"] == "finite-mode-spin-boson-dephasing"
    ]
    assert len(spin) == 1
    assert spin["t1_first_1_over_e_crossing_s"].isna().all()
    assert np.allclose(spin["minimum_excited_population"], 1.0, atol=1e-9)
