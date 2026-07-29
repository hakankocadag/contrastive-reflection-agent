import asyncio
from typing import Any

from .client import AsyncLLMClient
from .config import LLMConfig
from .prompts import build_system_prompt
from .schemas import PromptRule, StudentAgentOutput


class StudentAgent:
    """Analyzes graph data using an asynchronous LLM client."""

    def __init__(
        self,
        client: AsyncLLMClient,
        config: LLMConfig | None = None,
    ) -> None:
        self._client = client
        self._config = config or LLMConfig()

    async def analyze(
        self,
        graph_data: dict[str, Any],
        additional_rules: list[PromptRule] | None = None,
    ) -> StudentAgentOutput:
        """Analyzes graph data and returns validated structured output."""

        if not isinstance(graph_data, dict):
            raise TypeError("graph_data must be a dictionary")

        system_prompt = build_system_prompt(additional_rules)

        total_attempts = self._config.max_retries + 1
        last_error: Exception | None = None

        for attempt in range(total_attempts):
            try:
                raw_output = await asyncio.wait_for(
                    self._client.analyze(
                        graph_data=graph_data,
                        system_prompt=system_prompt,
                        config=self._config,
                    ),
                    timeout=self._config.timeout_seconds,
                )

                return StudentAgentOutput.model_validate(raw_output)

            except (TimeoutError, ConnectionError) as error:
                last_error = error

                if attempt == total_attempts - 1:
                    break

                retry_delay = 0.5 * (attempt + 1)
                await asyncio.sleep(retry_delay)

        raise RuntimeError(
            f"Student Agent request failed after {total_attempts} attempts"
        ) from last_error