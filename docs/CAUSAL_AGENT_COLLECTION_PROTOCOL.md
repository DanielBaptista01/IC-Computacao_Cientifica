# Protocolo de Coleta e Modelagem de Agentes Causais

## Objetivo

A unidade científica primária desta fase é uma representação física e matemática
parametrizada de um Agente Causal. O objetivo ainda não é treinar modelos.

## 1. Unidade de dado

Modelo causal: uma família $A_k(\boldsymbol{\theta})$.
Amostra: uma instanciação $A_k(\boldsymbol{\theta}_i,t_j,\rho_m)$.
Muitas amostras do mesmo modelo não aumentam a diversidade causal do catálogo.

## 2. Schema computacional

`CausalAgentModelRecord` registra fonte proposta, graus de liberdade, Hamiltonianos,
parâmetros, hipóteses, regime dinâmico, dinâmica efetiva, observáveis, métricas,
reversibilidade, domínio de validade, proveniência e maturidade.

`CausalAgentSampleRecord` representa somente uma instanciação.

Campos matemáticos usam estados explícitos: `value`, `not_applicable` e `unresolved`.
`unresolved` nunca significa ausência física.

## 3. Critérios de inclusão e exclusão

Um modelo entra no catálogo somente se possuir descrição física, proveniência,
parâmetros com unidades e domínio, separação entre causa e canal efetivo e aprovação
pelo validador. Modelos definidos apenas por nomes como `dephasing` ou `amplitude damping`
não constituem, por si só, Agentes Causais.

## 4. Proveniência

Toda expressão é marcada como `LITERATURE_DERIVED`, `AUTHOR_DERIVED`,
`NUMERICALLY_DERIVED`, `PHENOMENOLOGICAL` ou `HYPOTHETICAL`.

Literature-derived exige publicação, autores, ano, seção/equação, hipóteses e a
interpretação feita nesta IC. Uma derivação da IC não é apresentada como resultado
estabelecido da literatura.

## 5. Unidades

Usar SI para grandezas dimensionais. Grandeza adimensional usa unidade 1.
Frequência angular: $\mathrm{rad}\,\mathrm{s}^{-1}$. Tempo: $\mathrm{s}$. Uso de $\hbar=1$ deve ser explicitamente
declarado na configuração.

## 6. Regimes dinâmicos

Classificação inicial: `coherent_unitary`, `incoherent_cptp`, `general_open_system`.
Memória é registrada separadamente: `markovian`, `non_markovian`,
`mixed_or_crossover` ou `unresolved`.

## 7. Estados de prova

O conjunto inicial é $|0\rangle$, $|1\rangle$, $|+\rangle$, $|-\rangle$, $|+i\rangle$, $|-i\rangle$, cobrindo $\pm X$, $\pm Y$ e $\pm Z$.
A implementação está em `core/probes.py`.

## 8. Assinatura quantitativa

$\Sigma$ não é assumida como identidade única. Ela poderá reunir vetor de Bloch,
expectativas $\langle X\rangle/\langle Y\rangle/\langle Z\rangle$, entropia de von Neumann, pureza, coerência $\ell_1$ com base declarada,
fidelidade com alvo declarado, espectro, descritores Choi/superoperador e resposta temporal.

## 9. Parametrização

Todo parâmetro possui nome, símbolo, unidade, domínio físico e proveniência.
A regra de amostragem deve ser registrada por experimento. Varreduras não podem sair
silenciosamente do domínio de validade física.

## 10. Validação

Conforme aplicável, verificar:

$$
H=H^\dagger,\qquad U^\dagger U=I,\qquad \sum_j K_j^\dagger K_j=I,
$$

$$
\rho\succeq0,\qquad \operatorname{Tr}(\rho)=1.
$

Canais que deveriam ser físicos são verificados como CPTP.
Modelos numéricos posteriores devem declarar convergência, estabilidade e tolerâncias.

## 11. Versionamento e reprodutibilidade

Toda geração futura deve registrar versão do schema/experimento, commit SHA,
configuração integral e hash, ambiente Python e dependências relevantes, seed quando
houver estocasticidade e timestamp UTC.

## 12. Armazenamento

A camada de código usa `causal_agent_schema.py`, `provenance.py`, `registry.py`,
`validator.py` e `initial_catalog.py`. A árvore de dados separa catálogo/proveniência de
dados gerados. Grandes varreduras devem preferir artifacts ou releases.

## 13. Modelo causal versus amostra

`agent_id` identifica a família causal. `sample_id` identifica uma instanciação.
IDs, `source_name` e `channel_name` permanecem metadata e não entram automaticamente
nos vetores de entrada de ML.

## 14. Identificabilidade

A pergunta experimental é:

$$
A_i\neq A_j \quad\Longrightarrow?\quad \Sigma_i\neq\Sigma_j.
$$
A resposta pode ser negativa. O protocolo deve procurar pares distintos que sejam
indistinguíveis sob subconjuntos de estados/observáveis e registrar isso como
não-identificabilidade.

# Primeiro lote implementado

1. `coherent-longitudinal-detuning`: controle unitário reversível, útil para testar
perturbação com entropia preservada e recuperação por adjunto.

2. `finite-two-level-exchange-relaxation`: modelo microscópico finito com
$$
H_{\mathrm{int}}=i\hbar g\left(|01\rangle\langle10|-|10\rangle\langle01|\right).
$$

O agente é inicialmente preparado em $|0\rangle$. Após evolução conjunta unitária e traço parcial, o modelo reduzido produz `amplitude damping` com

$$
p(t)=\sin^2(gt).
$$

A cadeia implementada é

$$
\text{fonte/modelo}\to H_{\mathrm{int}}\to U_{SA}\to\operatorname{Tr}_A\to\mathcal E_t.
$$

O segundo é um baseline mecanístico controlado da IC. Não é silenciosamente rotulado
como vácuo eletromagnético ou outra fonte experimental específica.

# Próximo candidato

Reservatório bosônico estruturado/não-Markoviano. Ele só deverá entrar quando a
equação mestra, densidade espectral, parâmetros e domínio de validade da literatura
forem reproduzidos e testados, sem colapsar prematuramente o problema para um canal
canônico.

# Critério antes de geração massiva

Não gerar milhares de amostras até que os modelos e o protocolo passem pela suíte,
a exportação/versionamento esteja definida, a assinatura temporal esteja disponível,
exista experimento explícito de identificabilidade e a proveniência/configuração seja
capturada automaticamente.
