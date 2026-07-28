import asyncio
import json
from pathlib import Path
from typing import Any

from student_agent.agent import StudentAgent
from student_agent.schemas import StudentAgentOutput


class FakeLLMClient:
    """Temporary client used for testing without a real API."""

    async def analyze(
        self,
        graph_data: dict[str, Any],
        system_prompt: str,
    ) -> dict[str, Any]:
        assert graph_data["file_id"] == "sample-001"
        assert "Do not invent" in system_prompt
        assert "Ignore built-in function calls." in system_prompt

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


def load_mock_graph() -> dict[str, Any]:
    """Loads the temporary graph fixture used by the tests."""

    graph_path = Path(__file__).parent / "fixtures" / "mock_graph.json"

    with graph_path.open(encoding="utf-8") as file:
        return json.load(file)


def test_student_agent_returns_structured_output() -> None:
    agent = StudentAgent(client=FakeLLMClient())
    graph_data = load_mock_graph()

    result = asyncio.run(
        agent.analyze(
            graph_data=graph_data,
            additional_rules=["Ignore built-in function calls."],
        )
    )

    assert isinstance(result, StudentAgentOutput)
    assert len(result.detected_calls) == 1
    assert result.detected_calls[0].caller == "main"
    assert result.detected_calls[0].callee == "calculate_total"
    assert result.detected_calls[0].line_number == 8
    assert result.reported_errors == []