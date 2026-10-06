# FINAL_REVERSIBILITY_ANALYSIS

A classificacao e feita por condicao dinamica, nao como rotulo permanente da
familia. Distinguem-se unitariedade direta, invertibilidade linear, existencia
de inversa CPTP e nao-invertibilidade reduzida.

| agent_model_id | reversibility_class | condition_count | fraction_within_agent |
| --- | --- | --- | --- |
| coherent-longitudinal-detuning | class_I_direct_unitary_reversible | 405 | 1 |
| finite-mode-spin-boson-dephasing | class_II_analytically_invertible_numerically_effectively_singular_without_CPTP_inverse | 682 | 0.5262345679 |
| finite-mode-spin-boson-dephasing | class_II_linearly_invertible_without_CPTP_inverse | 590 | 0.4552469136 |
| finite-mode-spin-boson-dephasing | class_I_direct_unitary_reversible | 24 | 0.01851851852 |
| finite-two-level-exchange-relaxation | class_II_linearly_invertible_without_CPTP_inverse | 380 | 0.9382716049 |
| finite-two-level-exchange-relaxation | class_II_reduced_nonunitary_noninvertible | 10 | 0.02469135802 |
| finite-two-level-exchange-relaxation | class_I_direct_unitary_reversible | 15 | 0.03703703704 |
| markovian-photon-reservoir-decay | class_II_linearly_invertible_without_CPTP_inverse | 400 | 0.987654321 |
| markovian-photon-reservoir-decay | class_I_direct_unitary_reversible | 5 | 0.01234567901 |

Recuperacao condicionada, acesso ao ambiente e mitigacao nao sao inferidos
automaticamente a partir do superoperador reduzido.

No spin-boson finito, q(t)=exp[-Lambda(t)] permanece analiticamente positivo
para expoente finito. Regimes abaixo da tolerancia numerica de posto sao
registrados como analiticamente invertiveis e numericamente efetivamente
singulares, em vez de serem apresentados como singularidades matematicas exatas.
