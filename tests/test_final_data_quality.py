import csv
import json

import numpy as np
import pandas as pd

from ic_quantum.data.final_export import export_final_dataset
from ic_quantum.data.final_generator import generate_final_dataset_samples
from ic_quantum.data.final_protocol import FinalDatasetConfig
from ic_quantum.experiments.final_runner import run_final_pipeline


def _singular_and_ill_conditioned_config() -> FinalDatasetConfig:
    return FinalDatasetConfig(
        time_min_s=0.0,
        time_max_s=np.pi,
        time_points=2,
        probe_ids=("+",),
        coherent_detuning_rates=(0.5,),
        finite_exchange_couplings=(0.5,),
        photon_decay_rates=(0.2,),
        spin_boson_mode_counts=(64,),
        spin_boson_cutoffs=(2.0,),
        spin_boson_temperature_ratios=(1.0,),
    )


def test_spin_boson_reports_analytical_invertibility_separately_from_numeric_rank():
    samples = generate_final_dataset_samples(_singular_and_ill_conditioned_config())
    target = next(
        sample
        for sample in samples
        if sample.agent_model_id == "finite-mode-spin-boson-dephasing"
        and np.isclose(sample.time, np.pi)
    )
    descriptors = target.signature.channel_descriptors
    assert descriptors["analytical_linear_invertible"] is True
    if descriptors["numerical_linear_invertible_at_tolerance"] is False:
        assert descriptors["reversibility_class"] == (
            "class_II_analytically_invertible_"
            "numerically_effectively_singular_without_CPTP_inverse"
        )


def test_export_uses_strict_json_for_singular_channel_descriptors(tmp_path):
    config = _singular_and_ill_conditioned_config()
    samples = generate_final_dataset_samples(config)
    paths = export_final_dataset(samples, config, tmp_path)
    raw = paths["scientific_records_csv"].read_text(encoding="utf-8")
    assert "Infinity" not in raw
    assert "NaN" not in raw

    frame = pd.read_csv(paths["scientific_records_csv"])
    for value in frame["channel_descriptors_json"]:
        json.loads(
            value,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError(constant)
            ),
        )


def test_final_pipeline_writes_clean_csv_without_spurious_index_column(tmp_path):
    config = FinalDatasetConfig(
        time_min_s=0.0,
        time_max_s=0.2,
        time_points=2,
        probe_ids=("0", "+"),
        coherent_detuning_rates=(0.5,),
        finite_exchange_couplings=(0.5,),
        photon_decay_rates=(0.2,),
        spin_boson_mode_counts=(2,),
        spin_boson_cutoffs=(1.0,),
        spin_boson_temperature_ratios=(1.0,),
    )
    run_final_pipeline(tmp_path / "final", config)
    with (tmp_path / "final" / "tables" / "sample_counts.csv").open(
        encoding="utf-8"
    ) as handle:
        header = next(csv.reader(handle))
    assert header == ["agent_model_id", "sample_count"]
