import numpy as np

from ic_quantum.core.probes import FINAL_PROBE_IDS, final_probe_densities
from ic_quantum.data.final_generator import generate_final_dataset_samples
from ic_quantum.data.final_protocol import FinalDatasetConfig
from ic_quantum.data.state_encoding import decode_complex_matrix
from ic_quantum.core.validation import validate_density_matrix


def _small_config() -> FinalDatasetConfig:
    return FinalDatasetConfig(
        time_min_s=0.0,
        time_max_s=np.pi,
        time_points=5,
        probe_ids=("0", "+", "cube_ppp"),
        coherent_detuning_rates=(0.5,),
        finite_exchange_couplings=(0.5,),
        photon_decay_rates=(0.2,),
        spin_boson_mode_counts=(2,),
        spin_boson_cutoffs=(1.0,),
        spin_boson_temperature_ratios=(1.0,),
    )


def test_final_probe_ensemble_adds_symmetric_bloch_sphere_states():
    probes = final_probe_densities()
    assert len(FINAL_PROBE_IDS) == 14
    assert len(probes) == 14
    for rho in probes.values():
        validate_density_matrix(rho)
        assert np.isclose(np.real(np.trace(rho @ rho)), 1.0, atol=1e-10)


def test_final_dataset_config_expected_count():
    config = FinalDatasetConfig()
    assert config.expected_sample_count == 35154


def test_final_generator_covers_four_families_and_valid_ground_truth():
    config = _small_config()
    samples = generate_final_dataset_samples(config)
    assert len(samples) == 60
    assert len({sample.sample_id for sample in samples}) == 60
    assert {sample.agent_model_id for sample in samples} == {
        "coherent-longitudinal-detuning",
        "finite-two-level-exchange-relaxation",
        "markovian-photon-reservoir-decay",
        "finite-mode-spin-boson-dephasing",
    }
    for sample in samples:
        rho = decode_complex_matrix(sample.signature.extra["simulated_density_matrix"])
        validate_density_matrix(rho)
        assert "reversibility_class" in sample.signature.channel_descriptors
        assert len(sample.signature.choi_descriptors["choi_eigenvalues"]) == 4
        assert len(
            sample.signature.choi_descriptors["superoperator_singular_values"]
        ) == 4
