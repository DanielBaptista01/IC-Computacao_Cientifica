import json

import numpy as np
import pandas as pd

from ic_quantum.analysis.physical_v2_identifiability import (
    analyze_physical_signature_overlap,
    analyze_process_signature_overlap,
)
from ic_quantum.analysis.physical_v2_matched import (
    matched_em_thermal_dephasing_experiment,
)
from ic_quantum.core.validation import validate_density_matrix
from ic_quantum.data.physical_v2_export import export_physical_v2_dataset
from ic_quantum.data.physical_v2_generator import generate_physical_v2_samples
from ic_quantum.data.physical_v2_protocol import PhysicalV2Config
from ic_quantum.data.state_encoding import decode_complex_matrix
from ic_quantum.analysis.physical_v2_response import (
    mechanical_equal_ratio_frequency_experiment,
    summarize_thermal_characteristic_times,
)
from ic_quantum.dynamics.mechanical_phonon import thermal_truncation_tail_probability


def small_config():
    return PhysicalV2Config(
        probe_ids=("0", "1", "+", "-", "+i", "-i"),
        em_field_amplitudes_t=(1e-7,),
        em_drive_frequencies_hz=(0.0,),
        em_orientations=("z",),
        em_gaussian_sigma_b_t=(1e-7,),
        em_time_points=3,
        rabi_rates_hz=(1e5,),
        rabi_detunings_hz=(0.0,),
        rabi_phases_rad=(0.0,),
        rabi_time_points=3,
        thermal_mode_counts=(4,),
        thermal_cutoffs_rad_s=(1.0,),
        thermal_temperature_ratios=(0.5,),
        thermal_time_points=3,
        photon_decay_rates_s=(1e4,),
        photon_time_points=3,
        thermal_photon_decay_rates_s=(1e4,),
        thermal_photon_temperatures_k=(0.0, 0.05,),
        thermal_photon_time_points=3,
        mechanical_frequencies_hz=(1e9,),
        mechanical_couplings_hz=(1e6,),
        mechanical_temperatures_k=(0.0,),
        mechanical_mode_dimension=4,
        mechanical_time_points=3,
        mechanical_longitudinal_frequencies_hz=(1e6,),
        mechanical_longitudinal_couplings_hz=(1e5,),
        mechanical_longitudinal_occupations=(1.0,),
        mechanical_longitudinal_time_points=3,
        radiation_initial_xqp=(1e-5,),
        radiation_trapping_rates_s=(1e3,),
        radiation_time_points=3,
        charge_couplings_hz=(1e4,),
        charge_switching_rates_s=(1e4,),
        charge_time_points=3,
    )


def test_default_physical_v2_count_is_scientifically_scaled():
    assert PhysicalV2Config().expected_sample_count == 45920


def test_small_generator_covers_eight_nonredundant_sources_with_valid_density_matrices():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    assert len(samples) == config.expected_sample_count
    assert len({s.agent_model_id for s in samples}) == 8
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
    assert metadata["number_of_agent_families"] == 8
    assert (
        metadata["baseline_dataset"]["dataset_id"]
        == "ic_causal_agents_final_v1"
    )


def test_n_source_overlap_analysis_returns_all_twenty_eight_pairs():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    result = analyze_physical_signature_overlap(
        samples, atol=config.identifiability_atol
    )
    assert len(result["physical_pair_summary"]) == 28
    assert result["physical_mean_nearest_distance_matrix"].shape == (8, 8)


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
    assert len(states) == 8
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



def test_process_level_identifiability_covers_all_eight_agent_pairs():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    result = analyze_process_signature_overlap(
        samples, atol=config.identifiability_atol
    )
    assert len(result["process_pair_summary"]) == 28
    assert result["process_mean_nearest_distance_matrix"].shape == (8, 8)


def test_matched_em_thermal_snapshot_is_nonidentifiable_but_trajectory_differs():
    config = small_config()
    summary, trajectory = matched_em_thermal_dephasing_experiment(config)
    row = summary.iloc[0]
    assert row["max_probe_trace_distance_at_matched_snapshot"] < 1e-10
    assert row["endpoint_coherence_difference"] < 1e-10
    assert row["max_normalized_trajectory_coherence_difference"] > 1e-5
    assert len(trajectory) == 101


def test_thermal_response_includes_both_pure_dephasing_and_relaxation_mechanisms():
    config = small_config()
    samples = generate_physical_v2_samples(config)
    summary = summarize_thermal_characteristic_times(samples)
    agents = set(summary["agent_model_id"])
    assert {
        "finite-mode-spin-boson-dephasing",
        "thermal-photon-reservoir",
        "mechanical-phonon-mode",
        "single-mode-mechanical-phonon-dephasing",
    }.issubset(agents)
    pure = summary[
        summary["agent_model_id"].isin(
            {
                "finite-mode-spin-boson-dephasing",
                "single-mode-mechanical-phonon-dephasing",
            }
        )
    ]
    assert pure["t1_first_1_over_e_crossing_s"].isna().all()
    assert np.allclose(pure["minimum_excited_population"], 1.0, atol=1e-9)



def test_equal_dimensionless_mechanical_coupling_can_have_frequency_distinct_trajectory():
    config = small_config()
    # The compact config has only one longitudinal line, so construct the
    # targeted two-frequency grid without changing the rest of the test corpus.
    config = PhysicalV2Config(
        probe_ids=config.probe_ids,
        em_field_amplitudes_t=config.em_field_amplitudes_t,
        em_drive_frequencies_hz=config.em_drive_frequencies_hz,
        em_orientations=config.em_orientations,
        em_gaussian_sigma_b_t=config.em_gaussian_sigma_b_t,
        em_time_points=config.em_time_points,
        rabi_rates_hz=config.rabi_rates_hz,
        rabi_detunings_hz=config.rabi_detunings_hz,
        rabi_phases_rad=config.rabi_phases_rad,
        rabi_time_points=config.rabi_time_points,
        thermal_mode_counts=config.thermal_mode_counts,
        thermal_cutoffs_rad_s=config.thermal_cutoffs_rad_s,
        thermal_temperature_ratios=config.thermal_temperature_ratios,
        thermal_time_points=config.thermal_time_points,
        photon_decay_rates_s=config.photon_decay_rates_s,
        photon_time_points=config.photon_time_points,
        thermal_photon_decay_rates_s=config.thermal_photon_decay_rates_s,
        thermal_photon_temperatures_k=config.thermal_photon_temperatures_k,
        thermal_photon_time_points=config.thermal_photon_time_points,
        mechanical_frequencies_hz=config.mechanical_frequencies_hz,
        mechanical_couplings_hz=config.mechanical_couplings_hz,
        mechanical_temperatures_k=config.mechanical_temperatures_k,
        mechanical_mode_dimension=config.mechanical_mode_dimension,
        mechanical_time_points=config.mechanical_time_points,
        mechanical_longitudinal_frequencies_hz=(0.5e6, 1.0e6),
        mechanical_longitudinal_couplings_hz=(0.05e6, 0.10e6),
        mechanical_longitudinal_occupations=(1.0,),
        mechanical_longitudinal_time_max_s=2e-6,
        mechanical_longitudinal_time_points=21,
        radiation_initial_xqp=config.radiation_initial_xqp,
        radiation_trapping_rates_s=config.radiation_trapping_rates_s,
        radiation_time_points=config.radiation_time_points,
        charge_couplings_hz=config.charge_couplings_hz,
        charge_switching_rates_s=config.charge_switching_rates_s,
        charge_time_points=config.charge_time_points,
    )
    summary, trajectory = mechanical_equal_ratio_frequency_experiment(config)
    row = summary.iloc[0]
    assert np.isclose(
        row["coupling_a_hz"] / row["frequency_a_hz"],
        row["coupling_b_hz"] / row["frequency_b_hz"],
    )
    assert row["maximum_same_time_coherence_difference"] > 1e-5
    assert len(trajectory) == 21
