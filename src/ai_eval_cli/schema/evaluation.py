from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Controls the evaluator's internal posture while reasoning about transcripts."""

    thinking_level: Literal["low", "medium", "high"] = Field(
        "medium",
        description="How deep the LLM's thinking should be while analyzing (staff-level, high prompts).",
    )
    enforce_citations: bool = Field(
        True,
        description="If true, the LLM must populate every evidence field with verbatim transcript quotes.",
    )


class PhaseScore(BaseModel):
    """Represents an audit of a continuous workflow phase with source-backed evidence."""

    name: str = Field(
        ...,
        description="Phase name (e.g., Planning, Implementation, Debugging) that aligns with a coherent block of work.",
    )
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Numeric rating (1-10) reflecting how staff-level reasoning guided this phase.",
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence (0-100) in the transcript clarity for this phase.",
    )
    description: str = Field(
        ...,
        description="Summary of what happened, why it mattered, and how it aligned with architecture/context outcomes.",
    )
    highlights: List[str] = Field(
        ...,
        description="Positive behaviors annotated in this phase (e.g., scoping, prompt iterations).",
    )
    concerns: List[str] = Field(
        ...,
        description="Risks, uncertainty, or missing coverage noticed during the phase.",
    )
    evidence: List[str] = Field(
        ...,
        description="Verbatim transcript quotes or turn IDs that justify the phase rating; no paraphrasing.",
    )


class PromptEngineeringInsight(BaseModel):
    """Details how prompts were structured and the exact snippet that influenced the agent."""

    prompt_type: str = Field(
        ...,
        description="Prompt category (e.g., System Directive, Feedback Loop, Tool Call Instruction).",
    )
    effectiveness: int = Field(
        ...,
        ge=1,
        le=10,
        description="Staff-level judgment (1-10) of the prompt's clarity, context, and corrective power.",
    )
    rationale: str = Field(
        ...,
        description="Why the prompt was effective or lacking, citing context provision, hallucination fixes, or tooling alignment.",
    )
    examples: Optional[List[str]] = Field(
        None,
        description="Optional verbatim snippets that demonstrate the prompt style being evaluated.",
    )
    evidence: str = Field(
        ...,
        description="The exact prompt text (quoted) used to steer the agent; do not paraphrase.",
    )


class CapabilityScore(BaseModel):
    """Scores foundational capabilities with justification and direct evidence."""

    metric: str = Field(
        ...,
        description="Agentic capability being rated (e.g., Architecture Coherence, Debug Strategy, Retrieval Context).",
    )
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Rating (1-10) of how aptly the participant exhibited this capability.",
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence (0-100) associated with this capability score.",
    )
    rationale: str = Field(
        ...,
        description="Detailed explanation referencing planning, prompt correction, or safety trade-offs observed.",
    )
    evidence: List[str] = Field(
        ...,
        description="Quoted transcript excerpts or turn IDs validating the capability rating; no paraphrasing.",
    )


class TranscriptEvaluation(BaseModel):
    """Root schema representing the Gemini evaluation output for a transcript with evidence requirements."""

    transcript_id: str = Field(
        ...,
        description="Unique identifier for the transcript being evaluated (file stem, title, or provided ID).",
    )
    thought_process: str = Field(
        ...,
        description="Structured chain of thought describing how each score will be determined before outputting numbers.",
    )
    overall_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Overall Staff-level performance rating integrating architecture, context, and safety.",
    )
    config: ModelConfig = Field(
        default_factory=ModelConfig,
        description="Evaluation configuration that informs thinking depth and citation enforcement.",
    )
    capability_scores: List[CapabilityScore] = Field(
        ...,
        description="Detailed capability ratings (Architecture, Debugging, Retrieval, etc.) with evidence.",
    )
    timeline_phases: List[PhaseScore] = Field(
        ...,
        description="Ordered phases that highlight how agentic reasoning evolved with supporting evidence.",
    )
    prompt_engineering: List[PromptEngineeringInsight] = Field(
        ...,
        description="Insights about prompt design, including the exact text used and its effectiveness.",
    )
    recommendations: List[str] = Field(
        ...,
        description="Actionable next steps grounded in the transcript analysis.",
    )
    strengths: List[str] = Field(
        ...,
        description="Key strengths observed, especially around coordination, context provision, and safety awareness.",
    )
    evaluator_notes: Optional[str] = Field(
        None,
        description="Optional extra notes such as hallucination corrections referenced in the transcript.",
    )
