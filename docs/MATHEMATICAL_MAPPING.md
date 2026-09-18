# Correspondência entre formalismo matemático e implementação

Esta documentação separa resultados estabelecidos da literatura dos modelos controlados usados na infraestrutura da IC. Os exemplos canônicos abaixo são **baselines científicos**, não evidência de que a hipótese autoral do Agente Causal já esteja validada.

## Estado quântico

Para um estado puro, o código constrói explicitamente

\[
\rho = |\psi\rangle\langle\psi|.
\]

`core/states.py` implementa os estados de referência e `core/validation.py` verifica Hermiticidade, traço unitário e positividade semidefinida.

## Perturbação coerente

O primeiro controle positivo de reversibilidade é

\[
H_A = \frac{\hbar\omega}{2}\sigma_z,\qquad
U_A(t)=e^{-iH_At/\hbar},\qquad
\rho'=U_A\rho U_A^\dagger.
\]

`channels/unitary.py` define o Hamiltoniano e `dynamics/closed_system.py` calcula a exponencial matricial. A recuperação é testada com

\[
\rho_{rec}=U_A^\dagger\rho' U_A\approx\rho.
\]

## Canais quânticos

A dinâmica reduzida é calculada explicitamente por

\[
\mathcal E(\rho)=\sum_i K_i\rho K_i^\dagger,
\qquad
\sum_iK_i^\dagger K_i=I.
\]

`channels/` contém representações canônicas de dephasing, amplitude damping e depolarizing. `dynamics/open_system.py` implementa a soma de Kraus e a completude é testada numericamente.

Um canal não unitário não é rotulado simplesmente como "irreversível".

## Sistema global e sistema reduzido

O teste de dilatação de amplitude damping constrói uma dinâmica unitária em `S+A` e calcula

\[
\rho'_S=\operatorname{Tr}_A[U_{SA}(\rho_S\otimes\rho_A)U_{SA}^\dagger].
\]

O estado reduzido é comparado à representação de Kraus correspondente. Isso demonstra computacionalmente que unitariedade global não implica dinâmica unitária local.

## Superoperador e reversibilidade reduzida

Para a vetorização por colunas, a implementação usa

\[
\operatorname{vec}(K\rho K^\dagger)
=
(K^*\otimes K)\operatorname{vec}(\rho),
\]

de modo que o superoperador de um canal de Kraus é

\[
\mathbf S_{\mathcal E}
=
\sum_i K_i^*\otimes K_i.
\]

O módulo `dynamics/reversibility.py` então separa três perguntas matematicamente diferentes.

### 1. A transformação linear é invertível?

A invertibilidade linear é avaliada pela dimensão/rank de `\mathbf S_{\mathcal E}`. Quando o superoperador possui posto completo, existe `\mathbf S_{\mathcal E}^{-1}` como transformação linear.

Isso **não** significa que a inversa seja uma operação física admissível.

### 2. A inversa linear é CPTP?

Para avaliar complete positivity, é construída a matriz de Choi

\[
J(\mathcal E)
=
\sum_{ij}|i\rangle\langle j|
\otimes
\mathcal E(|i\rangle\langle j|).
\]

A complete positivity é verificada por

\[
J(\mathcal E)\succeq0,
\]

e a preservação do traço pela condição apropriada sobre o traço parcial da matriz de Choi.

Quando o canal é linearmente invertível, o mesmo teste é aplicado a `\mathcal E^{-1}`. Os canais canônicos usados no experimento, para parâmetros internos ao intervalo `0<p<1`, podem ser linearmente invertíveis sem que a inversa seja CPTP.

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

- Entropia de von Neumann: `S(rho) = -Tr(rho log_2 rho)`.
- Pureza: `P(rho) = Tr(rho^2)`.
- Fidelidade de Uhlmann: `F(rho,sigma) = [Tr sqrt(sqrt(rho) sigma sqrt(rho))]^2`.
- Coerência `l1`: `C_l1(rho) = sum_{i != j} |rho_ij|` na base computacional.

## Agente Causal

`agents/base.py` é uma abstração de dados da hipótese autoral. Ela mantém separados: identidade física proposta, modelo de interação, parâmetros, Hamiltoniano ou operadores de Kraus, canal efetivo e classe inicial de reversibilidade.

O código não assume que o nome de um canal identifica univocamente uma fonte física. Em particular, a infraestrutura deixa em aberto a pergunta científica de identificabilidade:

\[
A_a\neq A_b
\quad\text{pode coexistir com}\quad
\mathcal E_a=\mathcal E_b?
\]

Essa questão deverá ser investigada com dados temporais, parâmetros físicos, respostas a estados de prova e outras observáveis além da identificação nominal do canal.
