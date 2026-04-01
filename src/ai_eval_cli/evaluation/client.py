from __future__ import annotations

import time
from typing import List, Optional

from loguru import logger
from google import genai
from google.genai import errors

from ..config import CLIConfig
from ..ingestion.base import TranscriptPayload
from ..schema.evaluation import TranscriptEvaluation
from .prompts import build_eval_prompt

class GeminiEvaluator:
    """Wraps the Google Gemini API with lazy model resolution and Pydantic validation."""

    def __init__(self, config: CLIConfig):
        # The new SDK automatically handles auth via GENAI_API_KEY if not passed
        self.client = genai.Client(api_key=config.api_key)
        
        # Architectural Resilience: Resolve the model once at startup
        self.model_id = self._resolve_model(config.model_priority)
        logger.info("Connected: Using model %s", self.model_id)

    def _resolve_model(self, priority_list: List[str]) -> str:
        """
        Loops through the priority list and verifies existence.
        Returns the first valid model ID or raises an error.
        """
        for model_id in priority_list:
            try:
                # Lightweight check for model availability
                self.client.models.get(model=model_id)
                return model_id
            except errors.ClientError as e:
                if "404" in str(e):
                    logger.warning("Model %s not found. Falling back...", model_id)
                    continue
                raise e
        
        raise RuntimeError(f"None of the configured models are available: {priority_list}")

    def evaluate(self, payload: TranscriptPayload) -> TranscriptEvaluation:
        """Sends the transcript for evaluation with structured output enforcement."""
        prompt = build_eval_prompt(payload)

        try:
            # We use the resolved model_id here
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': TranscriptEvaluation,
                    'temperature': 0.0,
                }
            )

            if response.parsed:
                logger.success("Evaluation complete for %s", payload.transcript_id)
                return response.parsed
            
            raise ValueError("Gemini failed to return a parsed schema.")

        except Exception as exc:
            logger.error("Evaluation failed for %s: %s", payload.transcript_id, exc)
            raise