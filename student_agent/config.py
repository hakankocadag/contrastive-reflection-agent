from pydantic import BaseModel, ConfigDict, Field


class LLMConfig(BaseModel):
    """Defines provider-independent configuration for the LLM client."""

    model_config = ConfigDict(frozen=True)

    model_name: str = Field(
        default="mock-model",
        min_length=1,
        description="Name of the language model",
    )

    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Controls randomness in model responses",
    )

    max_output_tokens: int = Field(
        default=800,
        ge=1,
        le=8192,
        description="Maximum number of tokens allowed in the model response",
    )

    timeout_seconds: float = Field(
        default=30.0,
        gt=0.0,
        description="Maximum waiting time for one API request",
    )

    max_retries: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum number of retry attempts after a failed request",
    )