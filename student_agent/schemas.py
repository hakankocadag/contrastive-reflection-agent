from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    """Represents a function call detected in the analyzed code."""

    caller: str = Field(
        description="Name of the function making the call"
    )
    callee: str = Field(
        description="Name of the function being called"
    )
    line_number: int = Field(
        ge=1,
        description="Line number where the function call occurs",
    )


class ArchitectureError(BaseModel):
    """Represents an architectural error detected in the analyzed code."""

    error_type: str = Field(
        description="Type of the detected architectural error"
    )
    target_node: str = Field(
        description="AST node or function where the error was detected"
    )
    line_number: int = Field(
        ge=1,
        description="Line number where the error was detected",
    )


class StudentAgentOutput(BaseModel):
    """Defines the required structured output of the Student Agent."""

    detected_calls: list[FunctionCall] = Field(default_factory=list)
    reported_errors: list[ArchitectureError] = Field(default_factory=list)