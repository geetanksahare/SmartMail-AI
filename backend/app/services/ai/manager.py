from typing import TypeVar

from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.base import (
    AIProvider,
    AIProviderError,
)
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.groq_provider import GroqProvider


T = TypeVar("T", bound=BaseModel)


class AIServiceError(Exception):
    pass


class AIProviderManager:
    def __init__(self) -> None:
        self.providers: dict[str, AIProvider] = {
            "gemini": GeminiProvider(),
            "groq": GroqProvider(),
        }

        self.primary_provider = settings.AI_PRIMARY_PROVIDER
        self.fallback_provider = settings.AI_FALLBACK_PROVIDER

        self._validate_configuration()

    def _validate_configuration(self) -> None:
        if self.primary_provider not in self.providers:
            raise ValueError(
                f"Unknown primary AI provider: "
                f"{self.primary_provider}"
            )

        if self.fallback_provider not in self.providers:
            raise ValueError(
                f"Unknown fallback AI provider: "
                f"{self.fallback_provider}"
            )

        if (
            self.primary_provider
            == self.fallback_provider
        ):
            raise ValueError(
                "Primary and fallback providers "
                "must be different."
            )

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:

        primary = self.providers[
            self.primary_provider
        ]

        try:
            return primary.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=response_model,
            )

        except AIProviderError as primary_error:

            if not primary_error.retryable:
                raise AIServiceError(
                    "AI generation failed."
                ) from primary_error

            fallback = self.providers[
                self.fallback_provider
            ]

            try:
                return fallback.generate_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=response_model,
                )

            except AIProviderError as fallback_error:
                raise AIServiceError(
                    "All configured AI providers failed."
                ) from fallback_error


ai_manager = AIProviderManager()