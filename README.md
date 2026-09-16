# IC — Modelagem e Quantificação do Agente Causal

Base computacional da **segunda etapa da Iniciação Científica (2026)**. O objetivo desta fase é transformar o formalismo de Agente Causal, sistemas quânticos abertos, canais quânticos e métricas informacionais em experimentos reproduzíveis antes de qualquer treinamento de IA.

## Escopo científico desta versão

A cadeia implementada é:

`Agente Causal -> Interação -> Transformação Quântica -> rho' -> Métricas -> Classificação inicial da dinâmica`

Esta primeira versão **não prova a hipótese principal da IC**. Ela valida a infraestrutura matemática com modelos canônicos controlados: uma perturbação unitária em um qubit, dephasing, amplitude damping e depolarizing; além de uma dilatação unitária sistema+ambiente equivalente ao canal de amplitude damping.

## Estrutura

```text
src/ic_quantum/
├── core/          # estados, operadores e validação numérica
├── agents/        # abstração do Agente Causal e baselines canônicos
├── channels/      # canais unitários e representações de Kraus
├── metrics/       # entropia, pureza, fidelidade e coerência l1
├── dynamics/      # dinâmica fechada, aberta e traço parcial
├── experiments/   # experimentos reproduzíveis
└── data/          # schema dos registros experimentais
tests/             # testes científicos automatizados
docs/              # correspondência matemática -> código
results/           # saídas reproduzíveis do experimento inicial
```

## Instalação

```bash
git clone https://github.com/DanielBaptista01/IC-Computacao_Cientifica.git
cd IC-Computacao_Cientifica
git switch feat/fase2-base-modelagem
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale o pacote e as dependências de desenvolvimento:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Testes

```bash
pytest
```

Os testes verificam, entre outros pontos: estados densidade válidos, unitariedade, completude de Kraus, preservação da entropia por evolução unitária, reversão por `U^dagger`, redução de coerência por dephasing e equivalência entre uma dilatação global unitária e o canal reduzido de amplitude damping.

## Primeiro experimento

```bash
ic-first-experiment --output-dir results
```

ou

```bash
python -m ic_quantum.experiments.runner --output-dir results
```

Parâmetros padrão:

- `omega = 1.0`
- `time = 0.7`
- `p_dephasing = 0.35`
- `p_amplitude = 0.25`
- `seed = 20260916`

Saídas:

- `results/first_experiment.csv`
- `results/global_reduced_validation.json`

## Princípio de rigor

Toda funcionalidade deve seguir: definição matemática -> implementação -> teste analítico -> teste numérico -> experimento -> resultado. Modelos autorais permanecem hipóteses até que sejam formalmente testados e comparados contra baselines.

Consulte `docs/MATHEMATICAL_MAPPING.md` para as definições matemáticas implementadas.
