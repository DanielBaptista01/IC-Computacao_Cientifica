# Checkpoint de retomada — expansão físico-causal v2

Último checkpoint reconciliado antes do merge técnico com `main`.

## Estado

- Branch: `feat/agentes-fisicos-v2`
- PR: #6
- Baseline v1 permanece congelado: `ic_causal_agents_final_v1`.
- Catálogo autoritativo v2: `src/ic_quantum/data/physical_catalog.py`.
- Pipeline autoritativo v2: `physical_v2_protocol.py`,
  `physical_v2_generator.py`, `physical_v2_export.py`,
  `experiments/physical_v2_runner.py`.
- Os caminhos paralelos terminados em `_v2.py` são facades de compatibilidade,
  não uma segunda teoria/dataset.

## Implementado

Oito famílias/mecanismos físico-causais não redundantes:
campo magnético/EM coerente e quasistático; drive EM Rabi; spin-boson térmico;
reservatório fotônico térmico incluindo T=0 como limite; modo
mecânico-fonônico de troca; modo mecânico longitudinal; radiação
ionizante/quasipartículas (ponte fenomenológica); flutuador de carga RTN.

Análises:
- assinatura por estado;
- assinatura de processo por quatro probes independentes;
- reversibilidade por condição;
- tríade Agente–Ruído–Entropia;
- T1*/T2* como cruzamentos de 1/e;
- formas temporais de dephasing;
- experimento controlado de duas fontes distintas com o mesmo canal reduzido
  de dephasing em um snapshot.

## Próximos passos preservados em caso de interrupção

1. validar CI deste checkpoint;
2. criar merge commit com `main` mantendo a árvore científica reconciliada;
3. regenerar o dataset v2 e inspecionar tabelas/artefato;
4. gravar `PHYSICAL_V2_READINESS.md` com números extraídos do CI;
5. atualizar PR #6 e marcar pronta para revisão, sem merge automático.
