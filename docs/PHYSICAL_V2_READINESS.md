# Prontidão científico-computacional — expansão físico-causal v2

Checkpoint auditado: `eb30e10f07e0cff0dbe4a6c259c00e15649fd529`.
PR de consolidação: #6 (`feat/agentes-fisicos-v2` -> `main`).

## Matriz de requisitos

| Requisito | Status | Evidência ou limitação |
|---|---|---|
| Fonte física distinta de canal | DONE | Catálogo, schema e separação features/labels |
| Transformação causal latente com contexto físico | DONE | Testes e metadata |
| EM magnético e drive Rabi | DONE | Duas famílias com domínios explícitos |
| Banho térmico e fótons | DONE | Spin-boson finito e reservatório térmico |
| Vibrações/fônons | DONE | Modos quantizados transverso e longitudinal |
| Carga e defeito TLS | DONE | RTN de flutuador biestável |
| Radiação ionizante | PARTIAL | Dinâmica pós-impacto validada numericamente; deposição -> quasipartículas é PHENOMENOLOGICAL |
| Reversibilidade por condição | DONE | Mapas reduzidos, CPTP, limites unitários |
| Tríade agente–ruído–entropia | DONE | Tabelas e controle coerente |
| Identificabilidade e colisões | DONE | 28 pares, múltiplos probes e snapshot casado |
| Dataset v2 versionado e segregado | DONE | CSV/Parquet, manifest e SHA256, CI artifacts |
| Reprodutibilidade em CI | DONE | Execuções 37817701075 e 37817690978: success |
| Testes automatizados | DONE | 104 passed no run 37817701075 |
| Validação experimental em hardware | BLOCKED | Sem medições de dispositivo |
| Transporte microscópico completo de radiação | BLOCKED | Não há modelo/plataforma suficientes |
| Calibração universal E0/polarização -> Rabi | BLOCKED | Exige geometria e elementos de matriz |
| Vibração arbitrária de chassi e ensemble 1/f universal | BLOCKED | Não extrapolar modos selecionados |
| ML/QML | DONE | Não treinado, fora do escopo |
| Integração em main e release estável | PARTIAL | PR #6 permanece draft; integração requer decisão de merge |

## Evidência reexecutada

O GitHub Actions da branch, no commit auditado, concluiu com sucesso a suíte de
104 testes e produziu o artifact `ic-causal-agents-physical-v2` (aprox.
10,5 MB), além de regenerar o baseline v1. O resumo de CI reportou:

- Dataset: `ic_causal_agents_physical_v2`;
- N_A = 8 famílias não redundantes;
- N_S = 45.920 amostras;
- 28 pares entre fontes e 28 pares de assinatura multi-probe;
- distância de traço no snapshot EM/térmico casado = 0;
- diferença máxima das trajetórias normalizadas no exemplo casado ≈ 0,0002540933;
- diferença máxima de coerência mecânica no mesmo tempo sob comparação g/omega casada ≈ 0,2133721389;
- radiation_source_channel_bridge = PHENOMENOLOGICAL;
- machine_learning_trained = false.

Estes números são resultados de simulação do protocolo configurado, não medidas
de hardware, nem demonstração de identificabilidade universal. A diferença
temporal pequena no exemplo EM/térmico não deve ser apresentada como separação
robusta sem análise de ruído amostral, tolerância e incerteza.

## Critério de prontidão para redação

**PRONTO para redação científica com qualificações explícitas.** Usar o
manifest, as tabelas e a evidência gerados pelo pipeline, e não transcrever
valores de memória. O texto final deve separar literatura, proposta autoral,
simulação e validação experimental ausente.

**Não declarar release integrada** enquanto o PR #6 não for efetivamente
mesclado em `main`. O workflow de release condiciona sua publicação ao push
em `main`. Este documento registra o checkpoint, inclusive em caso de
interrupção posterior.

## Próximo passo operacional

Revisar PR #6, confirmar CI no novo HEAD após este commit e então decidir o
merge. A integração em main e publicação de release não são pressupostos para
validar numericamente a branch.
