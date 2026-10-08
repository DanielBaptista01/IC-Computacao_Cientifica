# Correspondência entre formalismo matemático e implementação

Esta documentação separa resultados estabelecidos da literatura dos modelos controlados usados na infraestrutura da IC. Os exemplos canônicos abaixo são **baselines científicos**, não evidência de que a hipótese autoral do Agente Causal já esteja validada.

## Estado quântico

Para um estado puro, o código constrói explicitamente

$$
\rho = |\psi\rangle\langle\psi|.
$$

`core/states.py` implementa os estados de referência e `core/validation.py` verifica Hermiticidade, traço unitário e positividade semidefinida.

## Perturbação coerente

O primeiro controle positivo de reversibilidade é

$$
H_A = \frac{\hbar\omega}{2}\sigma_z,\qquad
U_A(t)=e^{-iH_At/\hbar},\qquad
\rho'=U_A\rho U_A^\dagger.
$$

`channels/unitary.py` define o Hamiltoniano e `dynamics/closed_system.py` calcula a exponencial matricial. A recuperação é testada com

$$
\rho_{rec}=U_A^\dagger\rho' U_A\approx\rho.
$$

## Canais quânticos

A dinâmica reduzida é calculada explicitamente por

$$
\mathcal E(\rho)=\sum_i K_i\rho K_i^\dagger,
\qquad
\sum_iK_i^\dagger K_i=I.
$$

`channels/` contém representações canônicas de dephasing, amplitude damping e depolarizing. `dynamics/open_system.py` implementa a soma de Kraus e a completude é testada numericamente.

Um canal não unitário não é rotulado simplesmente como "irreversível".

## Sistema global e sistema reduzido

O teste de dilatação de amplitude damping constrói uma dinâmica unitária em `S+A` e calcula

$$
\rho'_S=\operatorname{Tr}_A[U_{SA}(\rho_S\otimes\rho_A)U_{SA}^\dagger].
$$

O estado reduzido é comparado à representação de Kraus correspondente. Isso demonstra computacionalmente que unitariedade global não implica dinâmica unitária local.

## Superoperador e reversibilidade reduzida

Para a vetorização por colunas, a implementação usa

$$
\operatorname{vec}(K\rho K^\dagger)
=
(K^*\otimes K)\operatorname{vec}(\rho),
$$

de modo que o superoperador de um canal de Kraus é

$$
\mathbf S_{\mathcal E}
=
\sum_i K_i^*\otimes K_i.
$$

O módulo `dynamics/reversibility.py` então separa três perguntas matematicamente diferentes.

### 1. A transformação linear é invertível?

A invertibilidade linear é avaliada pelo posto de $\mathbf S_{\mathcal E}$. Quando o superoperador possui posto completo, existe $\mathbf S_{\mathcal E}^{-1}$ como transformação linear.

Isso **não** significa que a inversa seja uma operação física admissível.

### 2. A inversa linear é CPTP?

Para avaliar complete positivity, é construída a matriz de Choi

$$
J(\mathcal E)
=
\sum_{ij}|i\rangle\langle j|
\otimes
\mathcal E(|i\rangle\langle j|).
$$

A complete positivity é verificada por

$$
J(\mathcal E)\succeq0,
$$

e a preservação do traço pela condição apropriada sobre o traço parcial da matriz de Choi.

Quando o canal é linearmente invertível, o mesmo teste é aplicado a $\mathcal E^{-1}$. Os canais canônicos usados no experimento, para parâmetros internos ao intervalo $0<p<1$, podem ser linearmente invertíveis sem que a inversa seja CPTP.

### 3. Existe inversão unitária direta sobre o sistema?

Um canal CPTP de mesma dimensão com representação de Choi de posto 1 corresponde, neste contexto, a uma evolução unitária. Esse caso é classificado como

`class_I_direct_unitary_reversible`.

Os casos canônicos não unitários são distinguidos entre:

- `class_II_linearly_invertible_without_CPTP_inverse`;
- `class_II_reduced_nonunitary_noninvertible`.

A categoria

`class_III_requires_structured_recovery_analysis`

é reservada para situações em que a análise requer informação adicional sobre condicionamento, memória, acesso ao ambiente, recuperação aproximada ou outra estrutura física não contida apenas no canal reduzido.

Essa taxonomia é uma ferramenta computacional da segunda etapa; ela não pretende resolver automaticamente problemas de recuperação condicionada ou correção de erros.

## Métricas

- Entropia de von Neumann: $S(\rho)=-\operatorname{Tr}(\rho\log_2\rho)$.
- Pureza: $P(\rho)=\operatorname{Tr}(\rho^2)$.
- Fidelidade de Uhlmann: $F(\rho,\sigma)=\left[\operatorname{Tr}\sqrt{\sqrt{\rho}\,\sigma\sqrt{\rho}}\right]^2$.
- Coerência $\ell_1$: $C_{\ell_1}(\rho)=\sum_{i\neq j}|\rho_{ij}|$ na base computacional.

## Agente Causal

`agents/base.py` é uma abstração de dados da hipótese autoral. Ela mantém separados: identidade física proposta, modelo de interação, parâmetros, Hamiltoniano ou operadores de Kraus, canal efetivo e classe inicial de reversibilidade.

O código não assume que o nome de um canal identifica univocamente uma fonte física. Em particular, a infraestrutura deixa em aberto a pergunta científica de identificabilidade:

$$
A_a\neq A_b
\quad\text{pode coexistir com}\quad
\mathcal E_a=\mathcal E_b?
$$

Essa questão deverá ser investigada com dados temporais, parâmetros físicos, respostas a estados de prova e outras observáveis além da identificação nominal do canal.

## Transformação Causal Latente entre profundidades

A hipótese computacional inter-depth é representada por

$$
\rho_{d+1}=G_{d+1}\circ\mathcal C_d\circ G_d(\rho_{d-1}).
$$

`dynamics/causal_latent.py` implementa `LatentCausalTransform`. A classe representa a transformação efetiva no intervalo e mantém `agent_id` separado da transformação. Portanto, o código não identifica a transformação observada com sua causa física por definição.

Isso preserva a possibilidade científica de dois Agentes Causais distintos produzirem a mesma dinâmica reduzida.

As representações atualmente suportadas são identidade, transformação unitária e canal CPTP por Kraus. A categoria `custom` existe para extensões futuras e não recebe automaticamente uma classe de reversibilidade.

### Recuperação unitária direta

Quando $\mathcal C_d(\rho)=U_d\rho U_d^\dagger$, a implementação retorna explicitamente $U_d^{-1}=U_d^\dagger$ e testa numericamente a recuperação do estado anterior. Esse é o controle positivo da hipótese de reversibilidade local.

### Limite de uma porta unitária após geração de mistura

Considere um alvo puro e um canal que produza um estado misto $\rho'$. Toda unitária aplicada somente ao sistema preserva o espectro de $\rho'$ e, portanto, também preserva sua pureza. Uma unitária pode rotacionar autovetores, mas não transformar um estado genuinamente misto em um estado puro.

Para um alvo puro, a maior fidelidade possível sob qualquer unitária sobre o sistema é:

$$
\max_U F(\rho_{\mathrm{target}},U\rho' U^\dagger)=\lambda_{\max}(\rho').
$$

Se $\lambda_{\max}(\rho')<1$, nenhuma porta unitária isolada sobre o sistema pode realizar recuperação perfeita.

`dynamics/reversibility.py` implementa esse limite em `max_unitary_recovery_fidelity_to_pure_target`.

No experimento mínimo, $G_1=H$ prepara $|+\rangle$, e o `dephasing` com $p=0{,}35$ produz autovalores $0{,}825$ e $0{,}175$. Logo, o limite de recuperação por qualquer unitária é $0{,}825<1$.

Essa conclusão é deliberadamente limitada a unitárias no sistema reduzido. Ela não implica impossibilidade de recuperação com acesso ao ambiente, informação lateral, redundância, condicionamento ou correção de erros.


---

# Extensão final do corpus científico

## Dephasing spin-boson finito

A família `finite-mode-spin-boson-dephasing` implementa

$$
H_S=\frac{\hbar\omega}{2}\sigma_z,\quad
H_A=\sum_k\hbar\Omega_k b_k^\dagger b_k,
$$
$$
H_{\mathrm{int}}=
\sum_k\hbar\lambda_k\sigma_z(b_k+b_k^\dagger).
$$

Na discretização térmica finita:

$$
\Lambda(t)=
\sum_k \frac{4\lambda_k^2}{\Omega_k^2}
[1-\cos(\Omega_k t)]
\coth\left(\frac{\Omega_k}{2T}\right),
$$

e

$$
\rho_{01}(t)=e^{-\Lambda(t)}\rho_{01}(0).
$$

A representação de Kraus equivalente é usada para validar a dinâmica reduzida.
Recorrências para frequências comensuráveis são tratadas como propriedade do
reservatório discreto implementado, não como afirmação universal sobre toda
dinâmica não-Markoviana.

## Reservatório fotônico Markoviano

A família `markovian-photon-reservoir-decay` modela um sistema de dois níveis
acoplado por troca de excitação a modos fotônicos. No limite Markoviano,
não dirigido e a temperatura zero:

$$
\dot\rho=
\gamma\left[
\sigma_-\rho\sigma_+
-\frac12\{\sigma_+\sigma_-,\rho\}
\right],
$$

com

$$
p(t)=1-e^{-\gamma t}.
$$

Amplitude damping é consequência da redução e não a identidade causal.

## Contraexemplo fonte versus canal

As famílias de troca finita e reservatório fotônico podem satisfazer

$$
\sin^2(gt)=1-e^{-\gamma t}=p,
$$

produzindo o mesmo canal reduzido. A infraestrutura testa essa igualdade em
todos os estados de prova. Portanto, `channel_name` não define Agente Causal.

## Assinatura final

$$
\Sigma =
\{
t,
\langle X\rangle,\langle Y\rangle,\langle Z\rangle,
S,P,C_{l_1},F,D,
\lambda(\rho),
\text{Choi},
\text{superoperador},
R
\}.
$$

Parâmetros físicos e identidade causal ficam no registro científico/metadata,
não em `observable_features`.

## Identificabilidade N-agentes

Para cada par $A_i,A_j$, estado e instante, todos os pontos paramétricos são
comparados por

$$
D(\rho_i,\rho_j)=\frac12\|\rho_i-\rho_j\|_1.
$$

São preservados mínimos, médias, medianas, máximos, regiões de colisão,
dependência de estado/tempo e variação intra-agente.

## Rigor numérico da reversibilidade

A análise genérica reporta a invertibilidade numérica sob tolerância explícita.
Para o spin-boson finito,

$$
q(t)=e^{-\Lambda(t)}>0
$$

para $\Lambda(t)$ finito. Assim, quando $q(t)$ cai abaixo da tolerância do teste de posto,
o regime é registrado como analiticamente invertível porém numericamente
efetivamente singular, evitando transformar condicionamento numérico em
não-invertibilidade matemática exata.

## Escopo epistemológico

Os resultados podem sustentar que os modelos estudados representam
fontes/mecanismos individualizáveis e que suas assinaturas são distinguíveis em
determinadas regiões. Também existem regiões de não-identificabilidade.

Não é demonstrado que toda fonte tenha assinatura única, que o sistema reduzido
sempre contenha informação causal suficiente, que o ambiente agregado seja um
formalismo inadequado, que exista recuperação universal ou que simulação
equivalha a validação em hardware.
