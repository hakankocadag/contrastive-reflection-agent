import asyncio
from typing import Any

import pytest
from pydantic import ValidationError

from student_agent.config import LLMConfig
from student_agent.wrapper import StudentAgentAPI


class WrapperFakeLLMClient:
    """Fake asynchronous client used to test the public API wrapper."""

    async def analyze(
        self,
        *,
        graph_data: dict[str, Any],
        system_prompt: str,
        config: LLMConfig,
    ) -> dict[str, Any]:
        assert graph_data["file_id"] == "wrapper-test-001"
        assert "Ignore Python built-in function calls." in system_prompt
        assert config.temperature == 0.0

        return {
            "detected_calls": [
                {
                    "caller": "main",
                    "callee": "process_data",
                    "line_number": 12,
                }
            ],
            "reported_errors": [],
        }


def test_wrapper_returns_json_compatible_dictionary() -> None:
    api = StudentAgentAPI(
        client=WrapperFakeLLMClient(),
        config=LLMConfig(
            temperature=0.0,
            max_output_tokens=500,
        ),
    )

    graph_data = {
        "file_id": "wrapper-test-001",
        "functions": [],
    }

    prompt_rules = [
        {
            "rule_id": "rule-001",
            "rule_text": "Ignore Python built-in function calls.",
            "version": 1,
        }
    ]

    result = asyncio.run(
        api.analyze_graph(
            graph_data=graph_data,
            prompt_rules=prompt_rules,
        )
    )

    assert isinstance(result, dict)
    assert result["detected_calls"][0]["caller"] == "main"
    assert result["detected_calls"][0]["callee"] == "process_data"
    assert result["detected_calls"][0]["line_number"] == 12
    assert result["reported_errors"] == []


def test_wrapper_rejects_invalid_prompt_rule() -> None:
    api = StudentAgentAPI(client=WrapperFakeLLMClient())

    invalid_rules = [
        {
            "rule_id": "rule-001",
            "rule_text": "Invalid version example.",
            "version": 0,
        }
    ]

    with pytest.raises(ValidationError):
        asyncio.run(
            api.analyze_graph(
                graph_data={"file_id": "wrapper-test-001"},
                prompt_rules=invalid_rules,
            )
        )