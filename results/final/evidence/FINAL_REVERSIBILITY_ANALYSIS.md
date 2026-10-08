# FINAL_REVERSIBILITY_ANALYSIS

A classificação e feita por condição dinâmica, não como rótulo permanente da
família. Distinguem-se unitariedade direta, invertibilidade linear, existência
de inversa CPTP e nao-invertibilidade reduzida.

| agent_model_id | reversibility_class | condition_count | fraction_within_agent |
| --- | --- | --- | --- |
| coherent-longitudinal-detuning | class_I_direct_unitary_reversible | 405 | 1 |
| finite-mode-spin-boson-dephasing | class_II_analytically_invertible_numérically_effectively_singular_without_CPTP_inverse | 682 | 0.5262345679 |
| finite-mode-spin-boson-dephasing | class_II_linearly_invertible_without_CPTP_inverse | 590 | 0.4552469136 |
| finite-mode-spin-boson-dephasing | class_I_direct_unitary_reversible | 24 | 0.01851851852 |
| finite-two-level-exchange-relaxation | class_II_linearly_invertible_without_CPTP_inverse | 380 | 0.9382716049 |
| finite-two-level-exchange-relaxation | class_II_reduced_nonunitary_noninvertible | 10 | 0.02469135802 |
| finite-two-level-exchange-relaxation | class_I_direct_unitary_reversible | 15 | 0.03703703704 |
| markovian-photon-reservoir-decay | class_II_linearly_invertible_without_CPTP_inverse | 400 | 0.987654321 |
| markovian-photon-reservoir-decay | class_I_direct_unitary_reversible | 5 | 0.01234567901 |

Recuperação condicionada, acesso ao ambiente e mitigação não sao inferidos
automaticamente a partir do superoperador reduzido.

No spin-boson finito, $q(t)=e^{-\Lambda(t)}$ permanece analiticamente positivo
para $\Lambda(t)$ finito. Regimes abaixo da tolerância numérica de posto são
registrados como analiticamente invertíveis e numéricamente efetivamente
singulares, em vez de serem apresentados como singularidades matemáticas exatas.
