# AI Assistant Evaluation CLI Plan

## Overview
We are building a lightweight Python CLI that ingests AI chat transcripts, evaluates them through Gemini 1.5 Pro/Flash against a strict schema, and surfaces the results as a rich dashboard focused on high-level agentic reasoning. The plan below outlines the directory layout, the Pydantic schema powering evaluations, and a phased implementation guide so you can review before any code is written.

## Proposed Directory Structure
```
/ (repo root)
├── README.md                   # overview, install/run instructions
├── PLAN.md                     # this plan (needs approval)
├── pyproject.toml / setup.cfg   # project metadata & dependencies
├── src/
│   └── ai_eval_cli/            # main package
│       ├── __init__.py
│       ├── ingestion/           # parsers for transcripts
│       │   ├── base.py
│       │   ├── markdown.py
│       │   └── json.py
│       ├── schema/              # Pydantic models and scoring logic
│       │   └── evaluation.py
│       ├── evaluation/          # Gemini integration + prompt builder
│       │   ├── client.py
│       │   ├── prompts.py
│       │   └── scoring.py
│       ├── cli/                 # rich dashboard & CLI entrypoints
│       │   ├── dashboard.py
│       │   └── runner.py
│       └── config.py            # credentials, schema config
├── tests/
│   ├── ingestion/              # fixture transcripts + parser tests
│   ├── evaluation/              # mocking Gemini responses + schema
│   └── cli/                    # CLI snapshot/render tests (rich console)
└── sample_transcripts/         # .md/.json fixture transcripts
```

## Evaluation Schema (Pydantic)
We will define a schema that captures agentic reasoning, iterative workflow, and promptcraft metrics. The root model `TranscriptEvaluation` looks like:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class PhaseScore(BaseModel):
    name: str
    score: int = Field(..., ge=1, le=10)
    confidence_score: float = Field(..., ge=0, le=100)
    description: str
    highlights: List[str]
    concerns: List[str]

class PromptEngineeringInsight(BaseModel):
    prompt_type: str
    effectiveness: int = Field(..., ge=1, le=10)
    rationale: str
    examples: Optional[List[str]]

class CapabilityScore(BaseModel):
    metric: str
    score: int = Field(..., ge=1, le=10)
    confidence_score: float = Field(..., ge=0, le=100)
    rationale: str

class TranscriptEvaluation(BaseModel):
    transcript_id: str
    overall_score: int = Field(..., ge=1, le=10)
    capability_scores: List[CapabilityScore]
    timeline_phases: List[PhaseScore]
    prompt_engineering: List[PromptEngineeringInsight]
    recommendations: List[str]
    strengths: List[str]
    evaluator_notes: Optional[str]
```

**Key capability metrics**: Architecture Coherence, Iterative Scoping & Planning, Technical Debts/Assertions, Debug Strategy, Retrieval + Context Provision, Gemina Promptism (ability to guide Gemini), Agentic Safety Considerations.

## Step-by-Step Implementation Guide
1. **Bootstrapping**
   - Initialize Python project (pyproject.toml with dependencies: `rich`, `pydantic`, `google-genai`, `tomli`, `loguru`).
   - Add README describing goal, prerequisites, sample usage.

2. **Ingestion Layer**
   - Implement `BaseTranscriptParser` abstract class in `ingestion/base.py`. It exposes `parse(path: Path) -> TranscriptPayload`.
   - Implement Markdown parser (read headings, blockquotes) and JSON parser (standard format). Normalize into shared `TranscriptPayload` dict containing timestamps, roles, message text.
   - Add tests using fixtures in `sample_transcripts/` to ensure both formats produce identical payloads.

3. **Schema Definition**
   - Build `schema/evaluation.py` with data models above and helper enums/constants for metric names.
   - Include validation rules for required fields, e.g., at least 3 capability scores, at least 2 timeline phases, overall score derived from metric averages (for local validation but can be overwritten if Gemini provides). Write tests ensuring serialization works.

4. **Gemini Integration**
   - Create `evaluation/prompts.py` to craft Gemini prompts with explicit instructions: include schema, scoring rubric, mention advanced metrics (architecture, prompts, safety). Use a structured template referencing `TranscriptPayload` summary.
   - Build `evaluation/client.py` as thin wrapper around `google.genai` (Gemini 1.5). Provide ability to inject API key via environment/config.
   - In `evaluation/scoring.py`, parse Gemini response JSON, validate via `TranscriptEvaluation`. Provide retry/logging strategy.
   - Write unit tests by mocking Gemini responses (use `unittest.mock` or `pytest-mock`).

5. **CLI + Dashboard**
   - Implement `cli/runner.py` CLI entrypoint (argparse or click) to accept one or more transcript paths, optionally override API options, output modes (raw JSON vs dashboard), and normalize responses for comparison.
   - Implement `cli/dashboard.py` using Rich `Console` + `Panel` + `Table` to display:
      * Overall score with sparklines.
      * Timeline phases with colored badges.
      * Strengths/improvements list.
      * Prompt engineering insights table.
      * A comparison table when multiple transcripts are provided, showing scores, key metrics, and differences side-by-side.
   - Allow `--dry-run` (skip Gemini, load cached sample evaluation for layout), `--json` for raw output.
   - Add CLI tests verifying table content (e.g., `rich` capture). Consider using `pytest` to capture console output.

6. **Glue + Configuration**
   - Support config file or env variables for Gemini API keys, API endpoint overrides.
   - Provide helper to cache evaluations locally for offline preview.
   - Document CLI commands and extension points.

7. **Completion & QA**
   - Add README usage instructions, sample command outputs screenshots.
   - Write `tests/` covering parsing, schema validation, CLI flows.
   - Optional: create GitHub Actions to run tests.
   - Reserve a section in `README.md` titled "Reflection: What Makes a Good AI-Assisted Workflow" for future narrative insights.

Please review this plan before I proceed with writing any code or scaffolding.
