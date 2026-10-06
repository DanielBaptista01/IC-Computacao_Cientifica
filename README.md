# IC — Modelagem e Quantificação do Agente Causal

Repositório computacional da Iniciação Científica de 2026 sobre modelagem e
quantificação de Agentes Causais em sistemas quânticos.

A formulação final preserva a teoria usual de sistemas abertos:

\[
\text{Ambiente} \supset \{A_1,A_2,\ldots,A_N\},
\]

e investiga se fontes ou mecanismos específicos presentes nessa descrição
agregada podem ser modelados individualmente pela cadeia

\[
\text{Fonte física}
\rightarrow A_k
\rightarrow H_{\mathrm{int}}^{(k)}
\rightarrow \mathcal E_k(t)
\rightarrow \rho_k(t)
\rightarrow \Sigma_k
\rightarrow R_k.
\]

O projeto não afirma unicidade universal da assinatura causal e não implementa
Machine Learning ou Quantum Machine Learning.

## Versão científica final

Identificador do dataset: ic_causal_agents_final_v1

Configuração:
experiments/configs/ic_causal_agents_final_v1.json

Comando de geração: ic-finalize

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

Nomes de canais, como dephasing e amplitude_damping, são descrições de dinâmica
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

observable_features exclui IDs causais, nomes de fonte/canal e parâmetros
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

\[
A_i\neq A_j \quad\Longrightarrow?\quad \Sigma_i\neq\Sigma_j.
\]

Todos os seis pares entre as quatro famílias são avaliados por estado, tempo e
combinações paramétricas. Regiões de colisão são preservadas como
não-identificabilidade.

Há ainda um experimento controlado em que a troca finita e o reservatório
fotônico Markoviano são parametrizados para gerar o mesmo canal reduzido de
amplitude damping. Portanto,

\[
\text{identidade do canal reduzido}
\not\Rightarrow
\text{identidade da fonte física}.
\]

## Agente Causal, ruído e entropia

A implementação mantém a distinção:

    Agente Causal = fonte/mecanismo modelado
    Ruído = efeito da interação em relação à computação/estado pretendido
    Entropia = grandeza informacional do estado

O controle coerente fornece perturbações observáveis com entropia preservada:

\[
\Delta S=0
\not\Rightarrow
\text{ausência de perturbação}.
\]

São analisadas entropia, pureza, coerência l1, fidelidade, distância de traço,
vetor de Bloch, espectro e descritores de Choi/superoperador.

## Reversibilidade

A classificação é feita por condição dinâmica (theta,t), não como rótulo
permanente da família. São distinguidas reversão unitária direta,
invertibilidade linear, inversa CPTP, não-invertibilidade reduzida e necessidade
de recuperação/mitigação estruturada.

No spin-boson finito, q(t)=exp[-Lambda(t)] é analiticamente positivo para
Lambda finito. Quando q fica abaixo da tolerância do teste numérico de posto, o
dataset registra separadamente a invertibilidade analítica e a singularidade
numérica efetiva.

## Transformação Causal Latente

A transformação física não programada continua representada por

\[
G_d \rightarrow \mathcal C_{k,d} \rightarrow G_{d+1}.
\]

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
hardware. A coerência l1 depende da base. A identificabilidade é condicional ao
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

A tag ic-2026-final e o dataset ic_causal_agents_final_v1 permanecem
congelados como baseline mecanístico. A expansão posterior aproxima o Agente
Causal das fontes físicas que motivaram a pesquisa e utiliza o identificador:

    ic_causal_agents_physical_v2

Famílias físico-causais validadas no v2:

1. external-magnetic-field-wave — componente magnética de campo/onda
   eletromagnética externa; inclui regime Zeeman coerente e ensemble
   longitudinal quasistático Gaussiano;
2. finite-mode-spin-boson-dephasing — reservatório bosônico térmico finito;
3. markovian-photon-reservoir-decay — reservatório eletromagnético de fótons;
4. mechanical-phonon-mode — modo mecânico/acústico quantizado acoplado ao
   qubit;
5. ionizing-radiation-quasiparticle-burst — radiação ionizante
   (raio cósmico/gama) condicionada à população de quasipartículas pós-impacto;
6. bistable-charge-fluctuator-rtn — armadilha/defeito de carga biestável com
   ruído telegráfico.

A família de radiação é explicitamente fenomenológica na ponte entre energia
depositada/geometria do evento e a condição inicial de quasipartículas. O código
não inventa um Hamiltoniano microscópico para esse trecho.

A geração v2 usa escalas temporais específicas de cada fonte. Por isso a análise
pairwise principal mede sobreposição de variedades de assinatura por
nearest-neighbour em distância de traço, em vez de equiparar artificialmente
tempos de microssegundos, milissegundos e unidades naturais.

Comando:

    ic-physical-v2 --config experiments/configs/ic_causal_agents_physical_v2.json --output-dir results/physical_v2

A saída separa novamente scientific_records, observable_features, causal_labels,
metadata e provenance. observable_features não inclui physical_source,
causal_mechanism, agent_model_id, regime físico ou parâmetros específicos do
simulador.

### Escopo físico ainda não fechado

Não foram promovidos a famílias validadas separadas:

- acoplamento elétrico de dipolo -d.E como família independente;
- transporte completo de partículas ionizantes e geometria de deposição;
- propagação espacial correlacionada em múltiplos qubits;
- ensemble completo de defeitos capaz de gerar um espectro 1/f;
- vibração macroscópica arbitrária de encapsulamento/chassi.

Esses casos permanecem extensões ou hipóteses, não resultados simulados.
