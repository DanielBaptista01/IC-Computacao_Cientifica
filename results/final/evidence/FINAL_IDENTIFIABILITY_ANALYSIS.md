# FINAL_IDENTIFIABILITY_ANALYSIS

A analise testa A_i != A_j =>? Sigma_i != Sigma_j sem assumir resposta positiva.
Para cada par de familias, estado de prova e tempo, todas as combinacoes dos
pontos parametricos foram comparadas pela distancia de traco. Uma condicao e
marcada como colisao quando existe ao menos um par parametrico abaixo da
tolerancia configurada.

| agent_a | agent_b | probe_time_conditions | conditions_with_collision | condition_collision_fraction | mean_condition_min_trace_distance | global_mean_trace_distance | max_trace_distance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| coherent-longitudinal-detuning | finite-mode-spin-boson-dephasing | 1134 | 198 | 0.1746031746 | 0.3155173782 | 0.362199974 | 1 |
| coherent-longitudinal-detuning | finite-two-level-exchange-relaxation | 1134 | 146 | 0.1287477954 | 0.1146121147 | 0.5062674269 | 1 |
| coherent-longitudinal-detuning | markovian-photon-reservoir-decay | 1134 | 94 | 0.08289241623 | 0.2530768676 | 0.5526629295 | 0.9999965127 |
| finite-mode-spin-boson-dephasing | finite-two-level-exchange-relaxation | 1134 | 122 | 0.1075837743 | 0.260335831 | 0.3972310838 | 1 |
| finite-mode-spin-boson-dephasing | markovian-photon-reservoir-decay | 1134 | 94 | 0.08289241623 | 0.2866797363 | 0.4124521431 | 0.9999965127 |
| finite-two-level-exchange-relaxation | markovian-photon-reservoir-decay | 1134 | 94 | 0.08289241623 | 0.0311617559 | 0.3646227758 | 0.9999965127 |

Regioes de colisao registradas: 748.

A existencia de colisoes e mantida como resultado cientifico. Os resultados
nao sustentam unicidade universal da assinatura causal no sistema reduzido.
