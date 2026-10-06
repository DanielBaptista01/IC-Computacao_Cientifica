# Protocolo de Geração em Escala — Dataset 001

## Problema científico

O primeiro dataset em escala deve investigar, sem Machine Learning, se dois modelos
causais já validados produzem assinaturas reduzidas distinguíveis sob um protocolo
controlado de estados, intensidades e tempos.

A hipótese é explicitamente interrogativa:

[
A_i \neq A_j \Longrightarrow? \Sigma_i \neq \Sigma_j.
]

## Famílias incluídas

1. `coherent-longitudinal-detuning`: perturbação coerente unitária.
2. `finite-two-level-exchange-relaxation`: agente quântico finito com evolução
   global unitária e relaxação reduzida após traço parcial.

Nenhum nome de canal é usado como identidade causal.

## Cobertura paramétrica

O Dataset 001 usa taxas de 0.5, 1.0 e 2.0 rad/s, 25 tempos uniformes em
[0, 2*pi] s e os seis estados de prova ±X, ±Y, ±Z.

A escolha é uma **faixa teórica normalizada**, não uma calibração de hardware.
Ela é motivada pelas variáveis adimensionais delta_omega*t e g*t:

- inclui identidade em t=0;
- inclui rotações coerentes parciais e ciclos completos;
- inclui troca completa de excitação em g*t=pi/2;
- inclui recorrências em g*t=n*pi;
- permite testar a degenerescência dinâmica de pares (rate,time) com o mesmo produto.

Assim, a grade não foi escolhida apenas para aumentar o número de linhas.

## Tamanho

Com 2 famílias, 3 taxas, 25 tempos e 6 estados:

[
N_S = 2\times3\times25\times6 = 900.
]

Esse é o primeiro corpus sistemático validado. Não constitui o corpus final da IC.

## Dados e separação futura de features

A execução produz:

- `validated_samples.csv`: registro científico completo;
- `observable_features.csv`: apenas grandezas observáveis/inferíveis e condições
  experimentais numéricas, sem agent_id e sem parâmetros do simulador;
- `labels.csv`: identidade causal separada;
- `dataset_metadata.json`: configuração, hash, commit, ambiente e dependências;
- `matched_identifiability_pairs.csv`: distância de traço entre famílias em
  condições pareadas;
- `dataset_analysis_summary.json`: N_A, N_S, cobertura e análise quantitativa.

## Assinatura inicial

Cada amostra preserva:

- vetor de Bloch de saída;
- entropia;
- pureza;
- coerência l1;
- fidelidade ao estado de entrada;
- distância de traço ao estado de entrada;
- espectro;
- descritores de reversibilidade do canal;
- matriz densidade simulada como ground truth científico.

A matriz densidade exata não deve ser interpretada como medição direta de hardware;
em um experimento físico ela exigiria inferência/tomografia.

## Análise de identificabilidade

Para condições com mesmo estado de prova, mesma taxa numérica e mesmo tempo,
calcula-se

[
D(\rho_i,\rho_j)=\frac12\|\rho_i-\rho_j\|_1.
]

Se D <= 1e-10, o par é registrado como não-identificável dentro desse protocolo.

Também é calculada, separadamente, a variação intra-agente entre passos temporais
adjacentes. A comparação entre média intra e inter é apenas descritiva e depende da
grade; ela não é usada como prova de unicidade causal.

## Critérios de interpretação

- não-identificabilidade é resultado, não erro;
- a separação observada vale somente no domínio desta grade e destas observáveis;
- parâmetros de taxa e tempo podem ser degenerados quando a dinâmica depende apenas
  do produto rate*time;
- nenhum classificador ou algoritmo de Machine Learning é treinado;
- o Dataset 001 serve para decidir quais extensões físicas e observáveis devem entrar
  no próximo lote.
