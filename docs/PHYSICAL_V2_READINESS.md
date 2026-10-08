# Prontidão científico-computacional — versão final consolidada

A versão oficial de encerramento desta Iniciação Científica é definida pela tag
`ic-2026-final-v2`. O workflow só cria essa tag/release em um `push` para
`main` depois de concluir a instalação, a suíte científica de testes, o
experimento inter-depth, o Dataset 001, o dataset mecanístico
`ic_causal_agents_final_v1` e o dataset físico-causal
`ic_causal_agents_physical_v2`.

Assim, a presença da tag `ic-2026-final-v2` é o critério computacional de
freeze: o SHA apontado pela tag é o commit oficial que deve ser citado no
Relatório Final. Releases anteriores (`ic-2026-final` e
`ic-2026-physical-v2`) permanecem como checkpoints históricos e não substituem
a versão consolidada.

## Estado científico congelado

O corpus físico-causal final contém 8 famílias não redundantes, 80 pontos
paramétricos, 14 estados de prova e 41 pontos temporais por ponto paramétrico,
totalizando 45.920 amostras no dataset físico-causal v2. A análise cobre os 28
pares possíveis entre as 8 famílias, além de uma assinatura operacional
multi-probe de processo.

A suíte científica no estado pré-freeze possui 104 testes automatizados. O
workflow de `main` deve repetir essa validação antes da criação da release
final; qualquer falha impede o freeze.

A radiação ionizante permanece explicitamente fenomenológica no elo entre
energia/geometria depositada e a condição inicial de quasipartículas. A ausência
de hardware, a restrição principal a um qubit, a ausência de shots/ruído de
leitura e os limites de identificabilidade permanecem limitações declaradas, não
resultados ocultados.

Nenhum modelo de Machine Learning ou Quantum Machine Learning é treinado nesta
IC.

## Reprodutibilidade

Os pacotes finais são gerados automaticamente e preservados na release
`ic-2026-final-v2`, incluindo:

`ic-causal-agents-final-v1.zip`,
`ic-causal-agents-physical-v2.zip`,
`FINAL_DATASET_MANIFEST.json`,
`FINAL_SUMMARY.json`,
`PHYSICAL_V2_MANIFEST.json` e
`PHYSICAL_V2_SUMMARY.json`.

O código-fonte completo é preservado pela própria tag. Os manifests registram os
hashes dos arquivos gerados e as configurações utilizadas.

Os comandos canônicos de reprodução são:

```bash
python -m pip install -e ".[dev]"
pytest
ic-finalize --config experiments/configs/ic_causal_agents_final_v1.json --output-dir results/final
ic-physical-v2 --config experiments/configs/ic_causal_agents_physical_v2.json --output-dir results/physical_v2
```

## Critério de encerramento

Quando a tag `ic-2026-final-v2` existir e apontar para o mesmo SHA da `main`
que concluiu o workflow `scientific-tests` com sucesso, a fase computacional
estará congelada e pronta para ser usada como fonte oficial do Relatório Final.
