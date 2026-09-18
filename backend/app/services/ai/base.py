from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class AIProviderError(Exception):
    def __init__(
        self,
        message: str,
        *,
        provider: str,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)

        self.provider = provider
        self.retryable = retryable
        self.status_code = status_code


class AIProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate structured output from the provider."""
        raise NotImplementedError