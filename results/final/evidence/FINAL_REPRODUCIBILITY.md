# FINAL_REPRODUCIBILITY

Versao do dataset: ic_causal_agents_final_v1
Commit capturado na geracao: 62502b7da297adf8c9bc10296ac662543019931f
Config SHA-256: 76d79a7eb22ff1d8a3873e6eb678eade27c859253a955b2261ee4d18cc1f3186

Comando canonico:

python -m pip install -e ".[dev]"
ic-finalize --config experiments/configs/ic_causal_agents_final_v1.json --output-dir results/final

A execucao grava o ambiente Python/pacotes em
environment/requirements-freeze.txt e hashes SHA-256 em
FINAL_DATASET_MANIFEST.json. A versao congelada do repositorio tambem fornece
requirements-lock.txt.
