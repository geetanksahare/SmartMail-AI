from typing import TypeVar

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Groq,
    RateLimitError,
)
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.base import AIProvider, AIProviderError


T = TypeVar("T", bound=BaseModel)


class GroqProvider(AIProvider):
    name = "groq"

    def __init__(self) -> None:
        self.model = settings.GROQ_MODEL

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "schema": response_model.model_json_schema(),
                        "strict": True,
                    },
                },
                reasoning_effort="low",
                temperature=0.7,
                max_completion_tokens=2000,
            )

        except RateLimitError as error:
            raise AIProviderError(
                "Groq rate limit reached.",
                provider=self.name,
                retryable=True,
                status_code=429,
            ) from error

        except APITimeoutError as error:
            raise AIProviderError(
                "Groq request timed out.",
                provider=self.name,
                retryable=True,
            ) from error

        except APIConnectionError as error:
            raise AIProviderError(
                "Could not connect to Groq.",
                provider=self.name,
                retryable=True,
            ) from error

        except APIStatusError as error:
            status_code = getattr(
                error,
                "status_code",
                None,
            )

            retryable = (
                status_code == 429
                or (
                    status_code is not None
                    and 500 <= status_code < 600
                )
            )

            raise AIProviderError(
                f"Groq request failed with status {status_code}.",
                provider=self.name,
                retryable=retryable,
                status_code=status_code,
            ) from error

        except Exception as error:
            raise AIProviderError(
                f"Groq request failed: {str(error)}",
                provider=self.name,
                retryable=True,
            ) from error

        content = response.choices[0].message.content

        if not content:
            raise AIProviderError(
                "Groq returned an empty response.",
                provider=self.name,
                retryable=False,
            )

        try:
            return response_model.model_validate_json(
                content
            )
        except Exception as error:
            raise AIProviderError(
                "Groq returned invalid structured output.",
                provider=self.name,
                retryable=False,
            ) from error