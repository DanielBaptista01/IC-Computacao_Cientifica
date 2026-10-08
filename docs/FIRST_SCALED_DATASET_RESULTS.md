# Resultados — Primeiro Dataset Científico em Escala

## Identificação do experimento

- dataset: `fase2_dataset_001`
- famílias causais: 2
- taxas por família: 3
- pontos temporais por taxa: 25
- estados de prova: 6
- amostras válidas: 900
- comparações inter-agente pareadas: 450
- treinamento de Machine Learning: **não realizado**

Os valores abaixo são resultados numéricos da execução automatizada do protocolo,
não afirmações estabelecidas pela literatura e não constituem prova de unicidade
causal.

## Hipótese testada

$
A_i \neq A_j \Longrightarrow? \Sigma_i \neq \Sigma_j.
$

O teste foi realizado comparando, para o mesmo estado de prova, a mesma taxa
numérica e o mesmo tempo, os estados reduzidos produzidos por:

1. `coherent-longitudinal-detuning`;
2. `finite-two-level-exchange-relaxation`.

A separação foi quantificada pela distância de traço.

## Resultado global de identificabilidade

Entre 450 pares:

- 125 apresentaram distância de traço <= 1e-10;
- fração não-identificável: 0.2777777778;
- distância inter-agente média: 0.3398406778;
- mediana: 0.2795084972;
- mínimo: 0;
- máximo: 1.

Logo, o primeiro dataset fornece simultaneamente exemplos distinguíveis e
não-distinguíveis. Isso rejeita qualquer interpretação de que a identidade causal
possa ser inferida universalmente de uma única assinatura reduzida neste protocolo.

## Dependência do estado de prova

### Estado $|0\rangle$

Todas as 75 comparações foram não-identificáveis dentro da tolerância.

- média: aproximadamente 5.9e-18;
- máximo numérico: aproximadamente 1.1e-16.

Isso ocorre porque, nos dois modelos implementados e com o agente de troca iniciado
em $|0\rangle$, o estado $|0\rangle$ é invariável. Portanto, esse estado de prova não contém poder
de distinção entre essas duas famílias.

### Estado $|1\rangle$

- média: 0.48;
- máximo: 1;
- 10/75 pares não-identificáveis.

O valor máximo 1 ocorre em condições de troca completa de excitação, nas quais a
dinâmica de relaxação leva $|1\rangle$ a $|0\rangle$, enquanto a perturbação longitudinal coerente
mantém as populações de $|1\rangle$.

### Estados equatoriais $|+\rangle$, $|-\rangle$, $|+i\rangle$, $|-i\rangle$

Cada um apresentou:

- média: 0.3897610167;
- máximo: 0.7071067812;
- 10/75 pares não-identificáveis.

O resultado confirma que a capacidade de identificar a família causal depende do
estado utilizado para interrogar a dinâmica.

## Separação intra-agente versus inter-agente

Na grade temporal utilizada, a distância de traço média entre pontos temporais
adjacentes foi:

- detuning coerente: 0.1010551926;
- troca/relaxação: 0.1275591168.

A distância média entre as duas famílias em condições pareadas foi 0.3398406778.

Assim, **nesta grade específica**, a separação inter-agente média excedeu a variação
local média entre passos temporais adjacentes de cada família. Esse resultado é
descritivo e dependente da discretização; não deve ser interpretado como prova de
separabilidade global das famílias.

## Não-identificabilidade paramétrica dentro da mesma família

Os testes também confirmaram que, nesses modelos,

$
\delta\omega t = \text{constante}
$

produz a mesma transformação coerente, e que

$
g t = \text{constante}
$

produz a mesma dinâmica reduzida do modelo de troca.

Portanto, um único estado final não permite, em geral, inferir separadamente taxa e
tempo de interação quando somente seu produto entra na dinâmica. Isso é um caso de
não-identificabilidade de parâmetros dentro da própria família causal.

## Reversibilidade dependente do regime

Nas 900 amostras:

- `class_I_direct_unitary_reversible`: 510;
- `class_II_linearly_invertible_without_CPTP_inverse`: 348;
- `class_II_reduced_nonunitary_noninvertible`: 42.

As 450 amostras do modelo coerente pertencem à Classe I. O modelo de troca,
entretanto, muda de classificação conforme $gt$:

- em recorrências com canal reduzido identidade, pode aparecer como Classe I;
- em regime intermediário, o mapa reduzido pode ser linearmente invertível, mas
  sem inversa CPTP;
- em troca completa, o canal reduzido torna-se não invertível.

Consequentemente, a classificação $R_k$ não deve ser tratada como rótulo imutável de
uma família causal; ela pode depender de parâmetros e tempo.

## Conclusão sustentada por este experimento

O resultado permitido é:

> As duas famílias causais controladas apresentam regiões do espaço experimental em
> que suas dinâmicas reduzidas são distinguíveis e regiões em que não são. O poder
> de distinção depende do estado de prova, do tempo e da intensidade. A
> identificabilidade causal é, portanto, uma propriedade do protocolo de observação e
> não uma consequência automática da existência de modelos físicos distintos.

## O que este experimento não demonstra

- que todos os Agentes Causais reais possuem assinaturas únicas;
- que duas fontes físicas reais distintas podem sempre ser identificadas pelo sistema
  reduzido;
- que 900 amostras determinísticas equivalem a evidência estatística experimental;
- robustez a shots, ruído de medição ou erro tomográfico;
- generalização para múltiplos qubits;
- superioridade operacional de uma estratégia de recuperação;
- qualquer resultado de Machine Learning.

## Próxima dependência científica

A expansão do número de linhas dentro destas duas famílias possui retorno científico
decrescente. O próximo ganho de diversidade deve vir da introdução de uma terceira
família fisicamente distinta, preferencialmente um modelo de dephasing com banho
bosônico ou outra fonte com estrutura temporal diferente, somente após reproduzir
suas equações, hipóteses, densidade espectral e domínio de validade da literatura.
