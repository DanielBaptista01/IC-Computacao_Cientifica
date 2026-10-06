"""One-command physical-source causal expansion pipeline v2."""

from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pandas as pd

from ic_quantum.analysis.final_identifiability import analyze_intra_agent_variation, analyze_pairwise_identifiability
from ic_quantum.analysis.final_reversibility import analyze_reversibility
from ic_quantum.analysis.triad import analyze_agent_noise_entropy, representative_temporal_metrics
from ic_quantum.analysis.final_plots import generate_final_plots
from ic_quantum.data.physical_catalog_v2 import build_physical_v2_registry
from ic_quantum.data.physical_export_v2 import export_physical_v2
from ic_quantum.data.physical_generator_v2 import generate_physical_v2_samples
from ic_quantum.data.physical_protocol_v2 import load_physical_v2_config


def _write(frame: pd.DataFrame, path: Path, preserve_index: bool=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=preserve_index)


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def run_physical_v2(output_dir: Path, config) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir/"tables").mkdir(parents=True,exist_ok=True)
    (output_dir/"figures").mkdir(parents=True,exist_ok=True)
    (output_dir/"evidence").mkdir(parents=True,exist_ok=True)

    samples=generate_physical_v2_samples(config)
    export_physical_v2(samples,config,output_dir)

    ident=analyze_pairwise_identifiability(samples,atol=config.identifiability_atol)
    intra=analyze_intra_agent_variation(samples,atol=config.identifiability_atol)
    triad_frame,triad_summary=analyze_agent_noise_entropy(samples,atol=config.identifiability_atol)
    representative=representative_temporal_metrics(triad_frame)
    rev_conditions,rev_summary=analyze_reversibility(samples)

    for name,frame in ident.items():
        _write(frame,output_dir/"tables"/f"{name}.csv",preserve_index=name in {"mean_min_distance_matrix","collision_fraction_matrix"})
    for name,frame in intra.items():
        _write(frame,output_dir/"tables"/f"{name}.csv")
    _write(triad_summary,output_dir/"tables"/"agent_noise_entropy_summary.csv")
    _write(representative,output_dir/"tables"/"representative_temporal_metrics.csv")
    _write(rev_conditions,output_dir/"tables"/"reversibility_by_condition.csv")
    _write(rev_summary,output_dir/"tables"/"reversibility_summary.csv")

    counts=(pd.Series([s.agent_model_id for s in samples],name="agent_model_id")
            .value_counts().rename_axis("agent_model_id").reset_index(name="sample_count")
            .sort_values("agent_model_id").reset_index(drop=True))
    _write(counts,output_dir/"tables"/"sample_counts.csv")
    parameter_counts=(pd.DataFrame([{"agent_model_id":s.agent_model_id,"parameter_point_id":s.metadata["parameter_point_id"]} for s in samples])
                      .drop_duplicates().groupby("agent_model_id",as_index=False).size()
                      .rename(columns={"size":"parameter_point_count"}))
    _write(parameter_counts,output_dir/"tables"/"parameter_coverage.csv")

    generate_final_plots(
        representative=representative,
        identifiability_matrix=ident["mean_min_distance_matrix"],
        collision_matrix=ident["collision_fraction_matrix"],
        reversibility_summary=rev_summary,
        probe_summary=ident["probe_summary"],
        intra_summary=intra["intra_summary"],
        pair_summary=ident["pair_summary"],
        sample_counts=counts,
        output_dir=output_dir/"figures",
    )

    registry=build_physical_v2_registry()
    source_status={
        "validated_level3":[
            {"agent_id":aid,"name":registry.get(aid).provisional_name,"physical_category":registry.get(aid).physical_category}
            for aid in registry.list_ids()
        ],
        "not_in_validated_dataset":[
            {"source":"cosmic-rays-ionizing-radiation","status":"HYPOTHETICAL/PHENOMENOLOGICAL","reason":"No project source currently closes the platform-specific chain energy deposition -> secondary excitations/quasiparticles -> validated reduced map."},
            {"source":"charge-noise-electric-fluctuations","status":"UNRESOLVED","reason":"No source-specific spectral density/transduction deltaV -> deltaH was validated for a selected platform."},
            {"source":"material-two-level-defects","status":"UNRESOLVED","reason":"Physical relevance acknowledged, but no project-grounded parameterized family reached LEVEL_3."},
            {"source":"quasiparticle-generation","status":"UNRESOLVED","reason":"No quantitatively validated generation/recombination-to-qubit map was established in the available corpus."},
        ],
    }
    (output_dir/"evidence"/"PHYSICAL_SOURCE_STATUS.json").write_text(json.dumps(source_status,indent=2,sort_keys=True),encoding="utf-8")

    pair=ident["pair_summary"]
    summary={
        "dataset_id":config.dataset_id,
        "N_A":int(len(counts)),
        "N_S":int(counts.sample_count.sum()),
        "parameter_points":int(parameter_counts.parameter_point_count.sum()),
        "pairwise_agent_pairs":int(len(pair)),
        "collision_regions":int(len(ident["collision_regions"])),
        "new_validated_physical_agents":[
            "external-electromagnetic-rabi-drive",
            "external-magnetic-zeeman-field",
            "thermal-photon-reservoir",
            "single-mode-mechanical-phonon-dephasing",
        ],
        "machine_learning_trained":False,
        "epistemic_guard":"Physical-source models are operational models with stated domains; no universal uniqueness and no hardware validation are claimed.",
    }
    (output_dir/"PHYSICAL_V2_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")

    (output_dir/"evidence"/"PHYSICAL_V2_RESULTS.md").write_text(
        "# PHYSICAL_V2_RESULTS\n\n"
        f"Dataset: {config.dataset_id}\n\n"
        f"Agentes validados no corpus combinado: {summary['N_A']}\n\n"
        f"Amostras validas: {summary['N_S']}\n\n"
        f"Pares causais analisados: {summary['pairwise_agent_pairs']}\n\n"
        f"Regioes de colisao de assinatura: {summary['collision_regions']}\n\n"
        "A v2 adiciona quatro fontes fisicas explicitamente modeladas: campo eletromagnetico coerente, campo magnetico Zeeman, reservatorio fotonico termico e modo mecanico/fononico. "
        "Raios cosmicos, ruido de carga, TLS materiais e quasiparticulas permanecem fora do corpus validado por falta de uma cadeia quantitativa completa no material cientifico disponivel.\n",
        encoding="utf-8",
    )

    (output_dir/"evidence"/"PHYSICAL_V2_IDENTIFIABILITY.md").write_text(
        "# PHYSICAL_V2_IDENTIFIABILITY\n\n"
        "A analise compara todas as familias pairwise por estado de prova, tempo e combinacoes parametricas usando distancia de traco. "
        "Colisoes sao preservadas como resultado de nao-identificabilidade. Consulte tables/pair_summary.csv, tables/collision_regions.csv e as matrizes em tables/.\n",
        encoding="utf-8",
    )
    (output_dir/"evidence"/"PHYSICAL_V2_REVERSIBILITY.md").write_text(
        "# PHYSICAL_V2_REVERSIBILITY\n\n"
        "A reversibilidade e classificada por condicao dinamica. Os campos EM e magnetico coerentes sao unitarios no dominio do modelo; reservatorios termicos e acoplamentos bosonicos reduzidos exigem a analise CPTP/linear ja existente. Consulte tables/reversibility_summary.csv.\n",
        encoding="utf-8",
    )

    manifest={}
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name!="PHYSICAL_V2_MANIFEST.json":
            manifest[str(path.relative_to(output_dir))]={"sha256":_sha256(path),"size_bytes":path.stat().st_size}
    (output_dir/"PHYSICAL_V2_MANIFEST.json").write_text(json.dumps({
        "dataset_id":config.dataset_id,"config_sha256":config.config_hash(),"files":manifest
    },indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="experiments/configs/ic_causal_agents_physical_v2.json")
    parser.add_argument("--output-dir",type=Path,default=Path("results/physical_v2"))
    args=parser.parse_args()
    run_physical_v2(args.output_dir,load_physical_v2_config(args.config))


if __name__=="__main__":
    main()
