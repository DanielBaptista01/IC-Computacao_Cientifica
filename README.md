# IC — Modelagem e Quantificação do Agente Causal

Repositório computacional da Iniciação Científica de 2026 sobre modelagem e
quantificação de Agentes Causais em sistemas quânticos.

A formulação final preserva a teoria usual de sistemas abertos:

$$
\text{Ambiente} \supset \{A_1,A_2,\ldots,A_N\},
$$

e investiga se fontes ou mecanismos específicos presentes nessa descrição
agregada podem ser modelados individualmente pela cadeia

$$
\text{Fonte física}
\rightarrow A_k
\rightarrow H_{\mathrm{int}}^{(k)}
\rightarrow \mathcal E_k(t)
\rightarrow \rho_k(t)
\rightarrow \Sigma_k
\rightarrow R_k.
$$

O projeto não afirma unicidade universal da assinatura causal e não implementa
Machine Learning ou Quantum Machine Learning.

## Versão científica final

Identificador do dataset: `ic_causal_agents_final_v1`

Configuração: `experiments/configs/ic_causal_agents_final_v1.json`

Comando de geração: `ic-finalize`

O Dataset 001 permanece preservado como experimento preliminar e não é o
dataset final.

O catálogo final contém quatro famílias:

1. coherent-longitudinal-detuning — perturbação longitudinal coerente e unitária;
2. finite-two-level-exchange-relaxation — grau de liberdade quântico finito com
   troca de excitação e relaxação reduzida;
3. finite-mode-spin-boson-dephasing — qubit longitudinalmente acoplado a banho
   bosônico térmico finito;
4. markovian-photon-reservoir-decay — relaxação radiativa Markoviana em
   reservatório fotônico.

Nomes de canais, como `dephasing` e `amplitude_damping`, são descrições de dinâmica
efetiva e não identidades causais.

## Dataset final

A configuração utiliza 4 famílias, 14 estados de prova, 81 pontos temporais,
5 pontos paramétricos para o agente coerente, 5 para a troca finita, 5 para o
reservatório fotônico e 16 para o spin-boson finito.

A geração produz 35.154 amostras válidas. Qualquer amostra que falhe no gate
matemático aborta a geração; não há descarte silencioso.

Estrutura:

    results/final/
    ├── dataset/
    │   ├── scientific_records.csv
    │   ├── scientific_records.parquet
    │   ├── observable_features.csv
    │   ├── observable_features.parquet
    │   ├── causal_labels.csv
    │   ├── causal_labels.parquet
    │   ├── metadata.json
    │   └── provenance.json
    ├── tables/
    ├── figures/
    ├── evidence/
    ├── environment/
    ├── config/
    ├── FINAL_DATASET_MANIFEST.json
    └── FINAL_SUMMARY.json

`observable_features` exclui IDs causais, nomes de fonte/canal e parâmetros
específicos do simulador capazes de revelar diretamente o rótulo. O registro
científico completo preserva parâmetros, proveniência e a matriz densidade
exata como ground truth de simulação.

## Instalação reproduzível

    git clone https://github.com/DanielBaptista01/IC-Computacao_Cientifica.git
    cd IC-Computacao_Cientifica
    python -m venv .venv

Ative o ambiente virtual e execute:

    python -m pip install --upgrade pip
    python -m pip install -r requirements-lock.txt
    python -m pip install -e . --no-deps

## Validação

    pytest

A suíte cobre estados densidade, Hermiticidade, unitariedade, Kraus, dinâmica
global/reduzida, reversibilidade, Choi/superoperadores, Transformação Causal
Latente, corpus/proveniência, quatro modelos finais, exportação e
identificabilidade.

## Reprodução integral

    ic-finalize --config experiments/configs/ic_causal_agents_final_v1.json --output-dir results/final

O pipeline gera dataset, tabelas, figuras, análise de identificabilidade,
reversibilidade, tríade Agente–Ruído–Entropia, metadata, proveniência, captura
do ambiente e hashes SHA-256.

O experimento inter-depth permanece reproduzível:

    ic-interdepth-experiment --output-dir results/interdepth

## Identificabilidade

A análise testa

$$
A_i\neq A_j \quad\Longrightarrow?\quad \Sigma_i\neq\Sigma_j.
$$

Todos os seis pares entre as quatro famílias são avaliados por estado, tempo e
combinações paramétricas. Regiões de colisão são preservadas como
não-identificabilidade.

Há ainda um experimento controlado em que a troca finita e o reservatório
fotônico Markoviano são parametrizados para gerar o mesmo canal reduzido de
amplitude damping. Portanto,

$$
\text{identidade do canal reduzido}
\not\Rightarrow
\text{identidade da fonte física}.
$$

## Agente Causal, ruído e entropia

A implementação mantém a distinção:

    Agente Causal = fonte/mecanismo modelado
    Ruído = efeito da interação em relação à computação/estado pretendido
    Entropia = grandeza informacional do estado

O controle coerente fornece perturbações observáveis com entropia preservada:

$$
\Delta S=0
\not\Rightarrow
\text{ausência de perturbação}.
$$

São analisadas entropia, pureza, coerência $\ell_1$, fidelidade, distância de traço,
vetor de Bloch, espectro e descritores de Choi/superoperador.

## Reversibilidade

A classificação é feita por condição dinâmica $(\boldsymbol{\theta},t)$, não como rótulo
permanente da família. São distinguidas reversão unitária direta,
invertibilidade linear, inversa CPTP, não-invertibilidade reduzida e necessidade
de recuperação/mitigação estruturada.

No spin-boson finito, $q(t)=e^{-\Lambda(t)}$ é analiticamente positivo para
$\Lambda(t)$ finito. Quando $q(t)$ fica abaixo da tolerância do teste numérico de posto, o
dataset registra separadamente a invertibilidade analítica e a singularidade
numérica efetiva.

## Transformação Causal Latente

A transformação física não programada continua representada por

$$
G_d \rightarrow \mathcal C_{k,d} \rightarrow G_{d+1}.
$$

Ela pode ser identidade, unitária, CPTP por Kraus ou extensão estruturada; não
é assumida como porta unitária em geral.

## Evidências para o Relatório Final

Usar como fontes primárias:

    results/final/evidence/FINAL_DATASET_MANIFEST.md
    results/final/evidence/FINAL_SCIENTIFIC_RESULTS.md
    results/final/evidence/FINAL_SCIENTIFIC_VALIDATION.md
    results/final/evidence/FINAL_IDENTIFIABILITY_ANALYSIS.md
    results/final/evidence/FINAL_REVERSIBILITY_ANALYSIS.md
    results/final/evidence/FINAL_REPRODUCIBILITY.md
    results/final/evidence/FINAL_LIMITATIONS.md
    results/final/FINAL_DATASET_MANIFEST.json
    results/final/FINAL_SUMMARY.json

Os números do Relatório Final devem ser extraídos desses arquivos e tabelas,
não recalculados manualmente.

## Limitações

A versão final é uma investigação computacional de um qubit e quatro famílias.
Não há hardware real, shots, erro de leitura ou tomografia experimental. Os
intervalos paramétricos são grades teóricas normalizadas, não calibrações de
hardware. A coerência $\ell_1$ depende da base. A identificabilidade é condicional ao
protocolo. Nenhum ML/QML foi treinado.

A Utunnel e o potencial estocástico pertencem à trajetória histórica da IC e
não são apresentados como resultados finais demonstrados.

## Princípio científico

    problema científico
    -> hipótese
    -> modelo matemático
    -> implementação
    -> validação
    -> experimento
    -> dados
    -> análise

Consulte docs/MATHEMATICAL_MAPPING.md e results/final/evidence/.



## Expansão físico-causal v2

A tag `ic-2026-final` e o dataset `ic_causal_agents_final_v1` permanecem
congelados como baseline mecanístico. A expansão físico-causal usa:

    ic_causal_agents_physical_v2

O catálogo reconciliado contém oito famílias/mecanismos causalmente distintos:

1. `external-magnetic-field-wave` — campo magnético externo: evolução Zeeman
   coerente e ensemble longitudinal quasistático;
2. `external-electromagnetic-rabi-drive` — onda EM coerente próxima à
   ressonância, com acoplamento efetivo de Rabi;
3. `finite-mode-spin-boson-dephasing` — banho bosônico térmico finito;
4. `thermal-photon-reservoir` — reservatório fotônico Markoviano cobrindo
   ($T=0$) e temperatura finita, com emissão e absorção;
5. `mechanical-phonon-mode` — modo acústico/mecânico quantizado com troca de
   excitação;
6. `single-mode-mechanical-phonon-dephasing` — modo vibracional quantizado com
   acoplamento longitudinal e dephasing recorrente;
7. `ionizing-radiation-quasiparticle-burst` — evento ionizante condicionado à
   dinâmica pós-impacto de quasipartículas;
8. `bistable-charge-fluctuator-rtn` — armadilha/defeito de carga biestável
   modelado por random-telegraph noise.

Essas famílias não são oito nomes de canais: cada entrada representa uma fonte/mecanismo físico documentado, não um rótulo de canal. O catálogo separa
`physical_source`, `causal_mechanism`, parâmetros físicos, dinâmica efetiva,
assinatura e reversibilidade. O modelo de radiação é explicitamente
`PHENOMENOLOGICAL` na ponte entre energia/geometria depositada e a condição
inicial de quasipartículas.

O drive EM coerente usa a taxa efetiva de Rabi $\Omega$. O projeto não inventa
uma conversão universal de $E_0$, polarização e momento de dipolo para
$\Omega$ sem uma plataforma física específica.

### Análises v2

O pipeline gera:
- assinaturas de estado por $\langle X\rangle$, $\langle Y\rangle$ e $\langle Z\rangle$, além de métricas informacionais;
- identificabilidade pairwise das variedades parâmetro-tempo;
- uma assinatura operacional de processo construída com quatro probes
  linearmente independentes $|0\rangle$, $|1\rangle$, $|+\rangle$ e $|+i\rangle$;
- um experimento controlado em que duas fontes físicas diferentes são
  parametrizadas para o mesmo canal reduzido de `dephasing` em um snapshot;
- reversibilidade por condição física;
- $T_1^*/T_2^*$ como primeiros cruzamentos de $1/e$, sem impor ajuste exponencial a
  dinâmicas recorrentes;
- comparação de mecanismos de dephasing;
- comparação de duas linhas espectrais mecânicas com mesma razão $g/\omega$ e mesma
  ocupação térmica.

A distância de processo usada no v2 é uma métrica operacional RMS baseada nas
saídas dos quatro probes, e **não** é apresentada como distância diamond.

### Reprodutibilidade

Comando:

    ic-physical-v2 --config experiments/configs/ic_causal_agents_physical_v2.json --output-dir results/physical_v2

A saída separa `scientific_records`, `observable_features`,
`causal_labels`, metadata e provenance. O conjunto `observable_features`
não inclui `agent_model_id`, `physical_source`, `causal_mechanism`, regime
físico nem parâmetros específicos do simulador.

### Limites não preenchidos artificialmente

Continuam fora do corpus validado:
- transporte microscópico completo de partículas ionizantes e a conversão
  universal de energia/localização depositada em $x_{\mathrm{qp}}(0)$;
- vibração macroscópica arbitrária de encapsulamento/chassi;
- ensemble completo de defeitos para reproduzir genericamente um espectro 1/f;
- calibração universal de campo elétrico bruto para uma taxa de Rabi;
- propagação espacial correlacionada em muitos qubits;
- validação experimental em hardware.

Esses pontos são limitações ou trabalhos futuros, não classes inventadas para
aumentar o dataset. Nenhum ML/QML é treinado nesta IC.


O modelo `markovian-photon-reservoir-decay` continua preservado no v1, mas
não é duplicado como rótulo causal no v2: ele é o limite $T=0$ da família
`thermal-photon-reservoir`.
