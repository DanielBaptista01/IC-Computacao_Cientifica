"""CSV/Parquet export for the physical-source v2 dataset."""

from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, timezone
import json, platform, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd, scipy

from ic_quantum.data.final_export import _feature_row, _strict_json, current_git_sha
from ic_quantum.data.physical_catalog_v2 import build_physical_v2_registry


def export_physical_v2(samples, config, output_dir: Path):
    dataset_dir=output_dir/"dataset"
    dataset_dir.mkdir(parents=True,exist_ok=True)
    registry=build_physical_v2_registry()
    scientific=[]
    features=[]
    labels=[]
    for row_id,sample in enumerate(samples):
        model=registry.get(sample.agent_model_id)
        metrics=sample.signature.informational_metrics
        obs=sample.signature.observables
        scientific.append({
            "row_id":row_id,"sample_id":sample.sample_id,
            "agent_model_id":sample.agent_model_id,
            "agent_name":model.provisional_name,
            "physical_source":sample.metadata["physical_source"],
            "causal_mechanism":sample.metadata["causal_mechanism"],
            "physical_category":model.physical_category,
            "maturity_level":model.maturity_level.value,
            "initial_system_state":sample.initial_system_state,
            "time_s":float(sample.time),
            "parameter_point_id":sample.metadata["parameter_point_id"],
            "parameter_values_json":_strict_json(sample.parameter_values),
            "physical_parameters_json":_strict_json(sample.signature.physical_parameters),
            "density_matrix_json":_strict_json(sample.signature.extra["simulated_density_matrix"]),
            "spectral_descriptors_json":_strict_json(sample.signature.extra.get("spectral_descriptors",{})),
            "output_bloch_x":float(obs["X"]),"output_bloch_y":float(obs["Y"]),"output_bloch_z":float(obs["Z"]),
            "entropy_after":float(metrics["entropy_after"]),"delta_entropy":float(metrics["delta_entropy"]),
            "purity_after":float(metrics["purity_after"]),"delta_purity":float(metrics["delta_purity"]),
            "coherence_l1_after":float(metrics["coherence_l1_after"]),"delta_coherence_l1":float(metrics["delta_coherence_l1"]),
            "fidelity_to_input":float(metrics["fidelity_to_input"]),"trace_distance_to_input":float(metrics["trace_distance_to_input"]),
            "state_spectrum_json":_strict_json(sample.signature.spectrum),
            "channel_descriptors_json":_strict_json(sample.signature.channel_descriptors),
            "choi_superoperator_descriptors_json":_strict_json(sample.signature.choi_descriptors),
            "reversibility_class":sample.signature.channel_descriptors["reversibility_class"],
            "representation_origin":sample.metadata["representation_origin"],
            "dataset_component":sample.metadata["dataset_component"],
            "random_seed":sample.random_seed,
        })
        features.append(_feature_row(row_id,sample))
        labels.append({
            "row_id":row_id,"sample_id":sample.sample_id,
            "agent_model_id":sample.agent_model_id,
            "physical_source":sample.metadata["physical_source"],
            "causal_mechanism":sample.metadata["causal_mechanism"],
        })

    frames={"scientific_records":pd.DataFrame(scientific),"observable_features":pd.DataFrame(features),"causal_labels":pd.DataFrame(labels)}
    paths={}
    for name,frame in frames.items():
        paths[name+"_csv"]=dataset_dir/(name+".csv")
        paths[name+"_parquet"]=dataset_dir/(name+".parquet")
        frame.to_csv(paths[name+"_csv"],index=False)
        frame.to_parquet(paths[name+"_parquet"],index=False)

    metadata={
        "dataset_id":config.dataset_id,"schema_version":config.schema_version,
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "git_commit_sha":current_git_sha(),"config":config.to_dict(),
        "config_sha256":config.config_hash(),"number_of_samples":len(samples),
        "number_of_agent_families":len({s.agent_model_id for s in samples}),
        "rejected_samples":0,"deterministic_dataset":True,"random_seed":None,
        "feature_policy":"observable_features excludes agent_model_id, physical_source, causal_mechanism, channel/source names and model-specific physical parameters; labels and scientific records remain separate.",
        "environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"scipy":scipy.__version__,"pandas":pd.__version__},
        "baseline_relation":"v1 remains frozen; v2 resamples the validated mechanistic families on a common time grid and adds four validated physical-source families.",
    }
    paths["metadata"]=dataset_dir/"metadata.json"
    paths["provenance"]=dataset_dir/"provenance.json"
    paths["metadata"].write_text(json.dumps(metadata,indent=2,sort_keys=True),encoding="utf-8")
    paths["provenance"].write_text(json.dumps(registry.to_dict(),indent=2,sort_keys=True,ensure_ascii=False),encoding="utf-8")
    return paths
