from typing import Any

from .agent import StudentAgent
from .client import AsyncLLMClient
from .config import LLMConfig
from .schemas import PromptRule


class StudentAgentAPI:
    """Provides a clean integration interface for the Student Agent."""

    def __init__(
        self,
        client: AsyncLLMClient,
        config: LLMConfig | None = None,
    ) -> None:
        self._agent = StudentAgent(
            client=client,
            config=config,
        )

    async def analyze_graph(
        self,
        graph_data: dict[str, Any],
        prompt_rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Analyzes graph data and returns a JSON-compatible dictionary.

        Prompt rules received from external modules are validated before
        being passed to the Student Agent.
        """

        validated_rules = [
            PromptRule.model_validate(rule)
            for rule in (prompt_rules or [])
        ]

        result = await self._agent.analyze(
            graph_data=graph_data,
            additional_rules=validated_rules,
        )

        return result.model_dump()