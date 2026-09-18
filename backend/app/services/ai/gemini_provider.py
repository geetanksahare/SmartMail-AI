from typing import TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.base import AIProvider, AIProviderError


T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self) -> None:
        self.model = settings.GEMINI_MODEL

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_model,
                    temperature=0.7,
                    max_output_tokens=2000,
                ),
            )

        except errors.APIError as error:
            status_code = getattr(error, "code", None)

            retryable = (
                status_code == 429
                or (
                    status_code is not None
                    and 500 <= status_code < 600
                )
            )

            raise AIProviderError(
                f"Gemini request failed: {error.message or str(error)}",
                provider=self.name,
                retryable=retryable,
                status_code=status_code,
            ) from error

        except Exception as error:
            raise AIProviderError(
                f"Gemini request failed: {str(error)}",
                provider=self.name,
                retryable=True,
            ) from error

        if getattr(response, "parsed", None) is not None:
            return response.parsed

        if not response.text:
            raise AIProviderError(
                "Gemini returned an empty response.",
                provider=self.name,
                retryable=False,
            )

        try:
            return response_model.model_validate_json(
                response.text
            )
        except Exception as error:
            raise AIProviderError(
                "Gemini returned an invalid structured response.",
                provider=self.name,
                retryable=False,
            ) from error