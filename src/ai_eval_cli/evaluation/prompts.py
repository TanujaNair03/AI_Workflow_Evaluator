from __future__ import annotations

from typing import Iterable

from loguru import logger

from ..ingestion.base import TranscriptMessage, TranscriptPayload


def build_eval_prompt(payload: TranscriptPayload) -> str:
    """Crafts the system + user prompt that instructs Gemini as a Staff-level evaluator."""

    messages = _format_messages(payload.messages)
    metadata = {
        "transcript_id": payload.transcript_id,
        **payload.metadata,
    }

    instruction = (
        "You are a Staff AI Systems Engineer evaluating a candidate's agentic workflow. Assess their architecture scoping, "
        "context provisioning, iterative reasoning, hallucination correction, and tooling coordination. Transcript speaker "
        "labels may be inconsistent (e.g., 'User', 'Claude', 'Agent', 'You'), so do not rely on specific labels—infer "
        "conversational turns and speaker identities purely from the context of the dialogue."
    )

    schema_guidance = (
        "Return a single JSON object that complies with the TranscriptEvaluation schema: "
        "overall_score (1-10), capability_scores, timeline_phases, prompt_engineering, recommendations, strengths, "
        "and optional evaluator_notes. ModelConfig rules must be enforced exactly—adhere strictly to the configured "
        "thinking_level and enforce_citations parameters. Every capability and phase score requires verbatim transcript "
        "quotes in the corresponding evidence fields with no paraphrasing."
    )

    prompt = (
        f"{instruction}\n\n"
        f"{schema_guidance}\n\n"
        f"Transcript metadata:\n{metadata}\n\n"
        f"Transcript messages:\n{messages}\n\n"
        "Be precise, cite the section that justifies each judgment, and produce clean JSON."
    )

    logger.debug("Built eval prompt for transcript %s", payload.transcript_id)
    return prompt


def _format_messages(messages: Iterable[TranscriptMessage]) -> str:
    # Ensuring we don't send empty text which can crash some SDK versions
    return "\n".join(f"{msg.role.upper()}: {msg.text.strip() or '[No text]'}" for msg in messages)
