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

Um canal não unitário não é rotulado simplesmente como "irreversível". A classificação inicial distingue a ausência de uma inversa global CPTP/unitária da possível existência de uma inversa apenas linear, recuperação condicionada ou recuperação com acesso adicional ao ambiente.

## Sistema global e sistema reduzido

O teste de dilatação de amplitude damping constrói uma dinâmica unitária em `S+A` e calcula

\[
\rho'_S=\operatorname{Tr}_A[U_{SA}(\rho_S\otimes\rho_A)U_{SA}^\dagger].
\]

O estado reduzido é comparado à representação de Kraus correspondente. Isso demonstra computacionalmente que unitariedade global não implica dinâmica unitária local.

## Métricas

- Entropia de von Neumann: `S(rho) = -Tr(rho log_2 rho)`.
- Pureza: `P(rho) = Tr(rho^2)`.
- Fidelidade de Uhlmann: `F(rho,sigma) = [Tr sqrt(sqrt(rho) sigma sqrt(rho))]^2`.
- Coerência l1: `C_l1(rho) = sum_{i != j} |rho_ij|` na base computacional.

## Agente Causal

`agents/base.py` é uma abstração de dados da hipótese autoral. Ela mantém separados: identidade física proposta, modelo de interação, parâmetros, Hamiltoniano ou operadores de Kraus, canal efetivo e classe inicial de reversibilidade. O código não assume que o nome de um canal identifica univocamente uma fonte física.
