"""Validated in-memory registry for causal-agent model families."""

from __future__ import annotations

import json
from pathlib import Path

from ic_quantum.data.causal_agent_schema import CausalAgentModelRecord
from ic_quantum.data.validator import CorpusValidationError, validate_model_record


class CausalAgentRegistry:
    """Registry of model families. Simulated samples belong in a separate dataset."""

    def __init__(self) -> None:
        self._models: dict[str, CausalAgentModelRecord] = {}

    def add(self, model: CausalAgentModelRecord) -> None:
        validate_model_record(model)
        if model.agent_id in self._models:
            raise CorpusValidationError(f"Duplicate causal-agent model: {model.agent_id}.")
        self._models[model.agent_id] = model

    def get(self, agent_id: str) -> CausalAgentModelRecord:
        try:
            return self._models[agent_id]
        except KeyError as exc:
            raise KeyError(f"Unknown causal-agent model: {agent_id}.") from exc

    def list_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._models))

    def to_dict(self) -> dict[str, dict]:
        return {agent_id: self._models[agent_id].to_dict() for agent_id in self.list_ids()}

    def save_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        return path
