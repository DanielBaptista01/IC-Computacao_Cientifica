# Auditoria da expansão físico-causal — v2

## Estado herdado

O dataset `ic_causal_agents_final_v1` permanece congelado como baseline mecanístico.
Ele já contém quatro famílias validadas: detuning coerente, troca finita de excitação,
spin-boson térmico finito e reservatório fotônico Markoviano.

## Lacuna científica

A taxonomia original da IC menciona fontes concretas como campos eletromagnéticos,
temperatura e vibração. A v1 implementa mecanismos úteis, mas ainda não separa
explicitamente todas essas origens físicas.

## Decisão de inclusão

Entram na v2 somente fontes para as quais há cadeia matemática completa e testável:

1. **campo eletromagnético externo coerente** — Hamiltoniano efetivo RWA de um
   sistema de dois níveis, com taxa de Rabi, detuning e fase;
2. **campo magnético externo (Zeeman)** — acoplamento `B·sigma`, mantendo campo e
   razão giromagnética explícitos;
3. **reservatório fotônico térmico** — equação mestra Markoviana com emissão
   estimulada/espontânea e absorção térmica, generalizando a família de temperatura zero;
4. **modo mecânico/fonônico quantizado** — oscilador bosônico longitudinalmente
   acoplado ao qubit, com frequência, acoplamento e ocupação térmica explícitos.

## Fontes não promovidas ao corpus validado

- **raios cósmicos/radiação ionizante**: o material do projeto disponível não fornece,
  para uma plataforma específica, uma cadeia quantitativa completa entre deposição de
  energia, quasipartículas e mapa reduzido. Permanece candidato HYPOTHETICAL/PHENOMENOLOGICAL.
- **ruído de carga**: há motivação física geral, mas não foi localizada no corpus
  atual uma parametrização de plataforma com densidade espectral e transdução
  `delta V -> delta H` suficiente para LEVEL_3.
- **defeitos/TLS materiais e quasipartículas**: permanecem candidatos de expansão,
  sem promoção para o dataset validado nesta revisão.

A ausência desses agentes é registrada como limitação, não preenchida por canais
canônicos arbitrários.
