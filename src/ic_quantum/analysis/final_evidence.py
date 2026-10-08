"""Generate evidence documents directly from final computed results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ic_quantum.data.final_catalog import build_final_registry


def _fmt(value: float) -> str:
    return f"{value:.10g}"


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in frame.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(_fmt(value))
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *rows])


def write_final_evidence(
    *,
    output_dir: Path,
    config,
    sample_counts,
    pair_summary,
    collision_regions,
    triad_summary,
    reversibility_summary,
    collision_experiment,
    metadata,
) -> list[Path]:
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    registry = build_final_registry()
    n_a = int(sample_counts.shape[0])
    n_s = int(sample_counts["sample_count"].sum())

    manifest_md = evidence_dir / "FINAL_DATASET_MANIFEST.md"
    manifest_md.write_text(
        f"""# FINAL_DATASET_MANIFEST

Dataset: `{config.dataset_id}`
Schema: `{config.schema_version}`
Commit de geração: `{metadata['git_commit_sha']}`
Famílias causais validadas: {n_a}
Amostras válidas: {n_s}
Amostras rejeitadas: {metadata['rejected_samples']}
Estados de prova: {len(config.probe_ids)}
Pontos temporais: {config.time_points}

O dataset separa `scientific_records`, `observable_features`, `causal_labels`,
`metadata` e `provenance`. Os hashes SHA-256 são registrados em
`FINAL_DATASET_MANIFEST.json`.

## Famílias

"""
        + "\n".join(
            f"- {agent_id} — {registry.get(agent_id).provisional_name} "
            f"({registry.get(agent_id).maturity_level.value})"
            for agent_id in registry.list_ids()
        )
        + "\n",
        encoding="utf-8",
    )

    ident_md = evidence_dir / "FINAL_IDENTIFIABILITY_ANALYSIS.md"
    ident_md.write_text(
        """# FINAL_IDENTIFIABILITY_ANALYSIS

A análise testa

$$
A_i\\neq A_j \\quad\\Longrightarrow?\\quad \\Sigma_i\\neq\\Sigma_j,
$$

sem assumir resposta positiva.
Para cada par de famílias, estado de prova e tempo, todas as combinações dos
pontos paramétricos foram comparadas pela distância de traço. Uma condição é
marcada como colisão quando existe ao menos um par paramétrico abaixo da
tolerância configurada.

"""
        + _markdown_table(
            pair_summary,
            [
                "agent_a",
                "agent_b",
                "probe_time_conditions",
                "conditions_with_collision",
                "condition_collision_fraction",
                "mean_condition_min_trace_distance",
                "global_mean_trace_distance",
                "max_trace_distance",
            ],
        )
        + f"""

Regiões de colisão registradas: {len(collision_regions)}.

A existência de colisões é mantida como resultado científico. Os resultados
não sustentam unicidade universal da assinatura causal no sistema reduzido.
""",
        encoding="utf-8",
    )

    reversibility_md = evidence_dir / "FINAL_REVERSIBILITY_ANALYSIS.md"
    reversibility_md.write_text(
        """# FINAL_REVERSIBILITY_ANALYSIS

A classificação é feita por condição dinâmica, não como rótulo permanente da
família. Distinguem-se unitariedade direta, invertibilidade linear, existência
de inversa CPTP e não-invertibilidade reduzida.

"""
        + _markdown_table(
            reversibility_summary,
            [
                "agent_model_id",
                "reversibility_class",
                "condition_count",
                "fraction_within_agent",
            ],
        )
        + """

Recuperação condicionada, acesso ao ambiente e mitigação não são inferidos
automaticamente a partir do superoperador reduzido.

No spin-boson finito, $q(t)=e^{-\\Lambda(t)}$ permanece analiticamente positivo
para $\\Lambda(t)$ finito. Regimes abaixo da tolerância numérica de posto são
registrados como analiticamente invertíveis e numericamente efetivamente
singulares, em vez de serem apresentados como singularidades matemáticas exatas.
""",
        encoding="utf-8",
    )

    coherent = triad_summary[
        triad_summary["agent_model_id"] == "coherent-longitudinal-detuning"
    ].iloc[0]
    max_collision_error = float(
        collision_experiment["max_trace_distance_across_probes"].max()
    )
    scientific_md = evidence_dir / "FINAL_SCIENTIFIC_RESULTS.md"
    scientific_md.write_text(
        f"""# FINAL_SCIENTIFIC_RESULTS

## Tríade Agente Causal–Ruído–Entropia

No controle coerente unitário, o máximo de $|\\Delta S|$ no corpus foi
{_fmt(float(coherent['max_abs_delta_entropy']))}, enquanto a máxima distância
de traço em relação à entrada foi
{_fmt(float(coherent['max_trace_distance_to_input']))}. Assim, a simulação
reproduz perturbações observáveis com entropia preservada.

"""
        + _markdown_table(
            triad_summary,
            [
                "agent_model_id",
                "samples",
                "max_trace_distance_to_input",
                "min_fidelity_to_input",
                "max_abs_delta_entropy",
                "max_abs_delta_purity",
                "max_abs_delta_coherence_l1",
                "fraction_perturbed_with_entropy_unchanged",
            ],
        )
        + f"""

## Colisão causal controlada

O modelo de troca finita e o reservatório fotônico Markoviano são modelos de
fonte distintos, mas foram parametrizados para produzir o mesmo canal de
`amplitude damping`. A maior distância de traço entre suas saídas, considerando
todos os estados de prova, foi {_fmt(max_collision_error)}.

Esse resultado demonstra, dentro dos modelos implementados, que identidade do
canal reduzido não implica identidade da fonte causal.

## Conclusão computacional permitida

Fontes/mecanismos específicos podem ser modelados individualmente e podem
produzir assinaturas distinguíveis em determinadas regiões. Também existem
regiões de não-identificabilidade; não se conclui unicidade universal.
""",
        encoding="utf-8",
    )

    dataset_results_md = evidence_dir / "FINAL_DATASET_RESULTS.md"
    dataset_results_md.write_text(
        f"""# FINAL_DATASET_RESULTS

Dataset: `{config.dataset_id}`
Familias causais: {n_a}
Amostras válidas: {n_s}
Amostras rejeitadas: {metadata['rejected_samples']}
Estados de prova: {len(config.probe_ids)}
Pontos temporais: {config.time_points}
Pares causais analisados: {len(pair_summary)}
Regioes de colisao de assinatura: {len(collision_regions)}

Este documento e um indice numerico compacto. As interpretacoes cientificas
estao em FINAL_SCIENTIFIC_RESULTS.md, FINAL_IDENTIFIABILITY_ANALYSIS.md e
FINAL_REVERSIBILITY_ANALYSIS.md. Os valores sao produzidos pelo pipeline, nao
inseridos manualmente.
""",
        encoding="utf-8",
    )

    validation_md = evidence_dir / "FINAL_SCIENTIFIC_VALIDATION.md"
    validation_md.write_text(
        """# FINAL_SCIENTIFIC_VALIDATION

Todos os modelos LEVEL_3 do catalogo final possuem proveniencia, hipoteses,
parametros/unidades, dominio de validade e metodo de validacao.

A suite automatizada verifica, conforme aplicavel, Hermiticidade de
Hamiltonianos, unitariedade, completude de Kraus, validade de estados, limites
nulos, solucoes analiticas, recorrencia do banho bosonico finito, equivalencia
microscopica/reduzida, separacao features/labels e colisoes causais construidas.

Qualquer falha aborta a geracao final; nao ha descarte silencioso.
""",
        encoding="utf-8",
    )

    reproducibility_md = evidence_dir / "FINAL_REPRODUCIBILITY.md"
    reproducibility_md.write_text(
        f"""# FINAL_REPRODUCIBILITY

Versão do dataset: `{config.dataset_id}`
Commit capturado na geracao: {metadata['git_commit_sha']}
Config SHA-256: {metadata['config_sha256']}

Comando canonico:

python -m pip install -e ".[dev]"
ic-finalize --config experiments/configs/ic_causal_agents_final_v1.json --output-dir results/final

A execucao grava o ambiente Python/pacotes em
environment/requirements-freeze.txt e hashes SHA-256 em
FINAL_DATASET_MANIFEST.json. A versao congelada do repositorio tambem fornece
requirements-lock.txt.
""",
        encoding="utf-8",
    )

    limitations_md = evidence_dir / "FINAL_LIMITATIONS.md"
    limitations_md.write_text(
        """# FINAL_LIMITATIONS

- Simulacao, nao hardware quantico real.
- Sistema principal restrito a um qubit.
- Quatro familias causalmente modeladas; nao e uma enumeracao de todas as fontes.
- Grades teoricas normalizadas, nao calibracoes de hardware.
- Ausencia de shots, erro de leitura e incerteza tomografica experimental.
- Matriz densidade exata e ground truth do simulador.
- Coerência $\\ell_1$ depende da base computacional.
- Identificabilidade e condicional ao protocolo investigado.
- Fontes distintas podem produzir o mesmo canal reduzido.
- O banho spin-boson finito modela memoria/recorrencias de um reservatorio discreto.
- Nenhum Machine Learning ou Quantum Machine Learning foi treinado.
- Utunnel permanece parte da evolucao historica, nao resultado final demonstrado.
""",
        encoding="utf-8",
    )

    return [
        manifest_md,
        ident_md,
        reversibility_md,
        scientific_md,
        dataset_results_md,
        validation_md,
        reproducibility_md,
        limitations_md,
    ]
