from typing import Any

from .prompts import build_system_prompt
from .schemas import PromptRule, StudentAgentOutput


class StudentAgent:
    """Analyzes graph data by using an asynchronous LLM client."""

    def __init__(self, client: Any) -> None:
        self._client = client

    async def analyze(
        self,
        graph_data: dict[str, Any],
        additional_rules: list[PromptRule] | None = None,
    ) -> StudentAgentOutput:
        """Analyzes graph data and returns validated structured output."""

        if not isinstance(graph_data, dict):
            raise TypeError("graph_data must be a dictionary")

        system_prompt = build_system_prompt(additional_rules)

        raw_output = await self._client.analyze(
            graph_data=graph_data,
            system_prompt=system_prompt,
        )

        return StudentAgentOutput.model_validate(raw_output)