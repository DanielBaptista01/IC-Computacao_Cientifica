# FINAL_SCIENTIFIC_RESULTS

## Tríade Agente Causal–Ruído–Entropia

No controle coerente unitário, o máximo de $|\Delta S|$ no corpus foi $8{,}00856626\times10^{-16}$, enquanto a máxima distância de traço em relação à entrada foi $1$. Assim, a simulação reproduz perturbações observáveis com entropia preservada.

| agent_model_id | samples | max_trace_distance_to_input | min_fidelity_to_input | max_abs_delta_entropy | max_abs_delta_purity | max_abs_delta_coherence_l1 | fraction_perturbed_with_entropy_unchanged |
| --- | --- | --- | --- | --- | --- | --- | --- |
| coherent-longitudinal-detuning | 5670 | 1 | 0 | 8.00856626e-16 | 6.661338148e-16 | 4.440892099e-16 | 1 |
| finite-mode-spin-boson-dephasing | 18144 | 0.5 | 0.5 | 1 | 0.5 | 1 | 0 |
| finite-two-level-exchange-relaxation | 5670 | 1 | 0 | 1 | 0.5 | 1 | 0.03928432517 |
| markovian-photon-reservoir-decay | 5670 | 0.9999965127 | 3.487342356e-06 | 0.9999971181 | 0.4999980024 | 0.9981325573 | 0 |

## Colisao causal controlada

O modelo de troca finita e o reservatorio fotonico Markoviano sao modelos de
fonte distintos, mas foram parametrizados para produzir o mesmo canal de
amplitude damping. A maior distância de traço entre suas saidas, considerando
todos os estados de prova, foi $2{,}220446049\times10^{-16}$.

Esse resultado demonstra, dentro dos modelos implementados, que identidade do
canal reduzido não implica identidade da fonte causal.

## Conclusão computacional permitida

Fontes/mecanismos específicos podem ser modelados individualmente e podem
produzir assinaturas distinguiveis em determinadas regiões. Também existem
regiões de nao-identificabilidade; não se conclui unicidade universal.
