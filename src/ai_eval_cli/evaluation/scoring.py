from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from loguru import logger
from pydantic import ValidationError

from ..schema.evaluation import TranscriptEvaluation


class ResponseParsingError(Exception):
    """Raised when a Gemini response cannot be coerced into the evaluation schema."""


def parse_gemini_response(response: Any) -> TranscriptEvaluation:
    """Extracts structured JSON from Gemini and validates it against the schema."""

    structured = _extract_structured_output(response)
    logger.debug("Gemini returned structured JSON for transcript data: %s", structured)

    try:
        evaluation = TranscriptEvaluation.model_validate(structured)
        logger.info("Gemini evaluation parsed for transcript %s", evaluation.transcript_id)
        return evaluation
    except ValidationError as exc:
        logger.error("Failed to validate Gemini response: %s", exc)
        raise ResponseParsingError("Gemini response failed schema validation.") from exc


def _extract_structured_output(response: Any) -> Mapping[str, Any]:
    candidates: Sequence[Any] = []

    if isinstance(response, dict):
        candidates = [response]
    else:
        for attr in ("structured_output", "content", "text", "output", "response"):
            value = getattr(response, attr, None)
            if value:
                candidates.append(value)
        if hasattr(response, "to_dict"):
            try:
                candidates.append(response.to_dict())
            except Exception:  # pragma: no cover
                logger.debug("Unable to convert response to dict for parsing.")

    for candidate in candidates:
        if isinstance(candidate, Mapping) and "transcript_id" in candidate:
            return candidate

        if isinstance(candidate, str):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, Mapping):
                return parsed

        if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes)):
            for item in candidate:
                if isinstance(item, Mapping) and "transcript_id" in item:
                    return item

    raise ResponseParsingError("Could not locate TranscriptEvaluation JSON in Gemini response.")
