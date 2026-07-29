import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from student_agent.agent import StudentAgent
from student_agent.config import LLMConfig
from student_agent.schemas import PromptRule, StudentAgentOutput


class FakeLLMClient:
    """Temporary asynchronous client used for normal tests."""

    def __init__(self) -> None:
        self.received_prompts: list[str] = []
        self.received_configs: list[LLMConfig] = []

    async def analyze(
        self,
        *,
        graph_data: dict[str, Any],
        system_prompt: str,
        config: LLMConfig,
    ) -> dict[str, Any]:
        self.received_prompts.append(system_prompt)
        self.received_configs.append(config)

        return {
            "detected_calls": [
                {
                    "caller": "main",
                    "callee": "calculate_total",
                    "line_number": 8,
                }
            ],
            "reported_errors": [],
        }


class RetryLLMClient:
    """Fails once and succeeds on the second attempt."""

    def __init__(self) -> None:
        self.attempts = 0

    async def analyze(
        self,
        *,
        graph_data: dict[str, Any],
        system_prompt: str,
        config: LLMConfig,
    ) -> dict[str, Any]:
        self.attempts += 1

        if self.attempts == 1:
            raise ConnectionError("Temporary connection error")

        return {
            "detected_calls": [],
            "reported_errors": [],
        }


class SlowLLMClient:
    """Simulates an API request that exceeds the timeout limit."""

    async def analyze(
        self,
        *,
        graph_data: dict[str, Any],
        system_prompt: str,
        config: LLMConfig,
    ) -> dict[str, Any]:
        await asyncio.sleep(0.1)

        return {
            "detected_calls": [],
            "reported_errors": [],
        }


def load_mock_graph() -> dict[str, Any]:
    """Loads the temporary graph fixture used by the tests."""

    graph_path = Path(__file__).parent / "fixtures" / "mock_graph.json"

    with graph_path.open(encoding="utf-8") as file:
        return json.load(file)


def test_student_agent_uses_latest_rule_version() -> None:
    client = FakeLLMClient()
    agent = StudentAgent(client=client)
    graph_data = load_mock_graph()

    rules = [
        PromptRule(
            rule_id="rule-001",
            rule_text="Ignore some built-in function calls.",
            version=1,
        ),
        PromptRule(
            rule_id="rule-001",
            rule_text="Ignore all Python built-in function calls.",
            version=2,
        ),
        PromptRule(
            rule_id="rule-002",
            rule_text="Do not report recursive calls as circular dependencies.",
            version=1,
        ),
    ]

    result = asyncio.run(
        agent.analyze(
            graph_data=graph_data,
            additional_rules=rules,
        )
    )

    prompt = client.received_prompts[0]
    received_config = client.received_configs[0]

    assert isinstance(result, StudentAgentOutput)
    assert len(result.detected_calls) == 1
    assert result.detected_calls[0].caller == "main"
    assert result.detected_calls[0].callee == "calculate_total"

    assert "Ignore all Python built-in function calls." in prompt
    assert "Ignore some built-in function calls." not in prompt
    assert "Do not report recursive calls as circular dependencies." in prompt

    assert received_config.temperature == 0.0
    assert received_config.max_output_tokens == 800


def test_student_agent_is_stateless() -> None:
    client = FakeLLMClient()
    agent = StudentAgent(client=client)
    graph_data = load_mock_graph()

    first_rules = [
        PromptRule(
            rule_id="rule-001",
            rule_text="First analysis rule.",
            version=1,
        )
    ]

    second_rules = [
        PromptRule(
            rule_id="rule-002",
            rule_text="Second analysis rule.",
            version=1,
        )
    ]

    asyncio.run(
        agent.analyze(
            graph_data=graph_data,
            additional_rules=first_rules,
        )
    )

    asyncio.run(
        agent.analyze(
            graph_data=graph_data,
            additional_rules=second_rules,
        )
    )

    first_prompt = client.received_prompts[0]
    second_prompt = client.received_prompts[1]

    assert "First analysis rule." in first_prompt
    assert "Second analysis rule." not in first_prompt

    assert "Second analysis rule." in second_prompt
    assert "First analysis rule." not in second_prompt


def test_student_agent_retries_after_connection_error() -> None:
    client = RetryLLMClient()

    config = LLMConfig(
        timeout_seconds=1.0,
        max_retries=1,
    )

    agent = StudentAgent(
        client=client,
        config=config,
    )

    result = asyncio.run(
        agent.analyze(graph_data=load_mock_graph())
    )

    assert isinstance(result, StudentAgentOutput)
    assert client.attempts == 2


def test_student_agent_stops_after_timeout() -> None:
    config = LLMConfig(
        timeout_seconds=0.01,
        max_retries=0,
    )

    agent = StudentAgent(
        client=SlowLLMClient(),
        config=config,
    )

    with pytest.raises(RuntimeError, match="failed after 1"):
        asyncio.run(
            agent.analyze(graph_data=load_mock_graph())
        )