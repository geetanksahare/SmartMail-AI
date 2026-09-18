from typing import Literal

from pydantic import BaseModel, Field


Tone = Literal[
    "professional",
    "friendly",
    "casual",
    "educational",
    "promotional",
]


NewsletterLength = Literal[
    "short",
    "medium",
    "long",
]


class AIGenerateRequest(BaseModel):
    topic: str = Field(
        min_length=3,
        max_length=500,
    )

    audience: str = Field(
        min_length=2,
        max_length=200,
    )

    tone: Tone = "professional"

    length: NewsletterLength = "medium"

    key_points: list[str] = Field(
        default_factory=list,
        max_length=10,
    )


class AIGenerateResponse(BaseModel):
    subject: str = Field(
        min_length=1,
        max_length=255,
    )

    preview_text: str = Field(
        min_length=1,
        max_length=300,
    )

    content: str = Field(
        min_length=1,
    )

    cta_text: str = Field(
        min_length=1,
        max_length=150,
    )


class AICampaignAnalysisResponse(BaseModel):
    summary: str = Field(
        min_length=1,
        max_length=2000,
    )

    strengths: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    issues: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    recommendations: list[str] = Field(
        default_factory=list,
        max_length=10,
    )