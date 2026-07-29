from typing import Any, Protocol, runtime_checkable

from .config import LLMConfig


@runtime_checkable
class AsyncLLMClient(Protocol):
    """Defines the interface required from an asynchronous LLM client."""

    async def analyze(
        self,
        *,
        graph_data: dict[str, Any],
        system_prompt: str,
        config: LLMConfig,
    ) -> dict[str, Any]:
        """Analyzes graph data and returns a dictionary response."""
        ...