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
├── dynamics/      # dinâmica fechada, aberta, traço parcial e reversibilidade
├── experiments/   # experimentos reproduzíveis
└── data/          # schema dos registros experimentais
tests/             # testes científicos automatizados
docs/              # correspondência matemática -> código
results/           # saídas reproduzíveis do experimento inicial
```

A lógica científica executável permanece dentro do pacote `src/ic_quantum`. Notebooks não são usados como fonte primária de verdade nesta etapa; quando forem adicionados, deverão consumir a API do pacote em vez de duplicar o formalismo.

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

Os testes verificam, entre outros pontos:

- estados densidade válidos;
- unitariedade;
- completude de Kraus;
- preservação da entropia por evolução unitária;
- reversão por `U^dagger`;
- redução de coerência por dephasing;
- equivalência entre uma dilatação global unitária e o canal reduzido de amplitude damping;
- diferença entre invertibilidade linear do superoperador e existência de inversa CPTP;
- classificação do caso unitário como reversível diretamente no sistema;
- não invertibilidade linear dos canais canônicos no limite de ruído máximo.

O workflow `scientific-tests` executa automaticamente a suíte em pushes para `main` e `feat/**`, e em pull requests para `main`.

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

O experimento registra entropia de von Neumann, pureza, coerência `l1`, fidelidade ao estado ideal e fidelidade após recuperação unitária quando aplicável.

## Diagnóstico de reversibilidade

A implementação não usa `"não unitário" = "irreversível"` como regra.

O módulo `dynamics/reversibility.py` constrói a representação de Liouville do canal e separa numericamente:

1. **invertibilidade linear do superoperador**;
2. **existência de inversa CPTP**;
3. **reversibilidade direta por uma unitária sobre o sistema observado**.

Assim, um canal pode possuir inversa como transformação linear e ainda assim sua inversa não ser um canal físico CPTP. Recuperação condicionada, acesso ao ambiente e mitigação aproximada permanecem explicitamente fora dessa classificação automática e exigem modelos adicionais.

## Reprodutibilidade

Os parâmetros experimentais são configuráveis pela linha de comando. Registros experimentais contêm o identificador do experimento, estado inicial, parâmetros do agente/canal e campo de seed. O primeiro experimento é determinístico; o campo de seed é mantido no schema para padronizar a infraestrutura que será usada quando processos estocásticos forem introduzidos.

Resultados não são inseridos manualmente no código de simulação. Eles são produzidos a partir dos modelos e métricas implementados.

## Princípio de rigor

Toda funcionalidade deve seguir:

`definição matemática -> implementação -> teste analítico -> teste numérico -> experimento -> resultado`

Modelos autorais permanecem hipóteses até que sejam formalmente testados e comparados contra baselines.

Consulte `docs/MATHEMATICAL_MAPPING.md` para as definições matemáticas implementadas.
