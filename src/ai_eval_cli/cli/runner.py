from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from rich.console import Console

from ..config import CLIConfig
from ..evaluation.client import GeminiEvaluator
from ..ingestion.json import JSONTranscriptParser
from ..ingestion.raw_text import RawTextTranscriptParser
from ..schema.evaluation import (
    CapabilityScore,
    PhaseScore,
    PromptEngineeringInsight,
    TranscriptEvaluation,
)
from .dashboard import render_comparison, render_single


_SUPPORTED_TRANSCRIPT_EXTENSIONS = frozenset({".json", ".md", ".txt"})


def main() -> None:
    console = Console()
    namespace = _parse_args()
    parsers = {
        ".json": JSONTranscriptParser(),
    }
    raw_text_parser = RawTextTranscriptParser()

    if namespace.dry_run:
        evaluator = None
    else:
        config = CLIConfig.from_env(namespace.api_key, namespace.model)
        evaluator = GeminiEvaluator(config=config)

    evaluations: List[TranscriptEvaluation] = []

    for path in namespace.transcripts:
        parser = parsers.get(path.suffix.lower(), raw_text_parser)
        payload = parser.parse(path)

        if namespace.dry_run:
            console.log(f"Dry run: skipping Gemini for {path.name}")
            evaluation = _mock_evaluation(payload.transcript_id)
        else:
            evaluation = evaluator.evaluate(payload)

        evaluations.append(evaluation)

    if namespace.json:
        console.print(json.dumps([eval.model_dump() for eval in evaluations], indent=2))
        return

    for evaluation in evaluations:
        render_single(console, evaluation)

    if len(evaluations) > 1:
        render_comparison(console, evaluations)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Eval CLI")
    parser.add_argument(
        "transcripts",
        nargs="+",
        type=_validate_transcript_path,
        help="Paths to transcript files (.md, .txt, or .json)",
    )
    parser.add_argument("--json", action="store_true", help="Dump raw JSON evaluations.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Bypass Gemini and use mock data to exercise the dashboard.",
    )
    parser.add_argument("--api-key", help="Gemini API key (overrides GENAI_API_KEY).")
    parser.add_argument("--model", help="Gemini model name (defaults from config).")
    return parser.parse_args()


def _validate_transcript_path(value: str) -> Path:
    path = Path(value)
    suffix = path.suffix.lower()
    if suffix not in _SUPPORTED_TRANSCRIPT_EXTENSIONS:
        supported = ", ".join(sorted(_SUPPORTED_TRANSCRIPT_EXTENSIONS))
        readable_suffix = suffix or "<no extension>"
        raise argparse.ArgumentTypeError(
            f"Unsupported transcript format '{readable_suffix}'. Supported extensions: {supported}."
        )
    return path


def _mock_evaluation(transcript_id: str) -> TranscriptEvaluation:
    return TranscriptEvaluation(
        transcript_id=transcript_id,
        thought_process="[Mock CoT] The transcript shows clear phase separation. The agent proactively asked for missing schema data in Turn 2, demonstrating Staff-level context gathering. Assigning an 8/10.",
        overall_score=8,
        capability_scores=[
            CapabilityScore(
                metric="Architecture Coherence",
                score=8,
                confidence_score=90.0,
                rationale="Solid breakdown of microservices boundaries and failure modes.",
                evidence=["[Turn 4] Agent: 'Let's separate the retrieval logic from the generation node to avoid context window overflow.'"]
            ),
            CapabilityScore(
                metric="Context Provision",
                score=7,
                confidence_score=85.0,
                rationale="Provided dataset schema and relevant constraints.",
                evidence=["[Turn 2] Agent: 'Please provide the exact JSON schema for the user table before we proceed.'"]
            ),
        ],
        timeline_phases=[
            PhaseScore(
                name="Planning",
                score=8,
                confidence_score=88.0,
                description="Scoped LangGraph pipeline, clarified roles, and defined success criteria.",
                highlights=[
                    "Merged architecture and dataset context into the top-level prompt.",
                    "Elevated potential failure modes before implementation.",
                ],
                concerns=["Could have captured explicit performance budgets earlier."],
                evidence=[
                    "[Turn 1] User initiates Planning phase.",
                    "[Turn 3] Agent delivers sequence diagram for the LangGraph nodes."
                ]
            ),
        ],
        prompt_engineering=[
            PromptEngineeringInsight(
                prompt_type="System Directive",
                effectiveness=8,
                rationale="Guide explicitly mapped responsibilities to the model.",
                examples=["You are the AI Architect ..."],
                evidence="System: 'You are the Principal Agent Architect. Do not write code until the user approves the architecture document.'"
            )
        ],
        recommendations=[
            "Log prompts/outputs for future audits.",
            "Add explicit recovery steps when tool calls fail.",
        ],
        strengths=[
            "Clear architecture scoping.",
            "Proactive context provisioning for Gemini.",
        ],
        evaluator_notes="Mock evaluation for UI testing.",
    )

if __name__ == "__main__":
    main()
