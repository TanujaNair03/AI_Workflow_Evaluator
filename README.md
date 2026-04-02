# 🧠 AI Workflow Evaluator

This CLI audits **the process and workflow** inside AI coding transcripts—how engineers scope architecture, contextualize prompts, iterate reasoning, and steer Gemini—rather than simply validating the outputted code.

---

## ✨ Features

- **Evidence-based grading:** Every phase, capability, and prompt insight collects verbatim transcript quotes via the `evidence` fields before any score is held. This keeps the evaluation transparent and auditable.
- **Pydantic-driven schema:** Gemini’s output is forced to comply with `TranscriptEvaluation`, which bundles `thought_process`, `ModelConfig`, capability ratings, timeline phases, prompt engineering insights, strengths, and recommendations in a single structured JSON.
- **Gemini thinking budget:** `ModelConfig.thinking_level` (low/medium/high) instructs the LLM to adopt a deeper chain-of-thought when you need Staff-level analysis; the schema also enforces citation discipline via `enforce_citations`.

## 📦 Installation

```bash
python -m pip install -e .
```

Then set your Gemini credentials:

```bash
export GENAI_API_KEY="ya29.xyz..."
```

Optionally override the model with:

```bash
export GENAI_MODEL="gemini-1.5-flash"
```

`ai-eval` respects the explicit config you supply; no hidden auto-fallbacks exist, so point it at the tier you want (e.g., `gemini-2.5-pro` for a legacy endpoint).

## ⚙️ Configuration

`CLIConfig` loads the API key and model name from arguments or the environment, defaulting to `gemini-1.5-flash`. If you want to target Gemini 2.5, just set `GENAI_MODEL=gemini-2.5-pro` before running the CLI. There is no automatic downgrade—the model you specify is the endpoint that will be contacted.

## 🚀 Usage

```bash
ai-eval evaluate transcript.md
```

Use `--dry-run` to exercise the Rich UI locally or `--json` to emit raw `TranscriptEvaluation` JSON.

*(Note: You can find 2 real-world sample transcripts required for this assignment inside the `/transcripts/real_world_transcripts` folder of this repository).* 


### 🐕 Meta-Evaluation (Dogfooding)

To stress-test the CLI, we ran it against the AI chat transcript that documented the creation of `ai-eval-cli` itself. It successfully handled the raw JSON ingestion path, exercised the model fallback logic, and accurately audited the prompt engineering dialogue from its own build. Below is the terminal output from that dogfooding run (insert the provided log here).

```bash
─────────────────────────────────────────────────────────────────── Transcript: gemini-chat ───────────────────────────────────────────────────────────────────
╭─────────────────────────────────────────────────────────────────────── Overall Score ───────────────────────────────────────────────────────────────────────╮
│                                                                            9/10                                                                             │
╰───────────────────────────────────────────────────────────────── Staff-level effectiveness ─────────────────────────────────────────────────────────────────╯
                                                                       Capability Scores                                                                       
╭──────────────────────────┬────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Metric                   │ Score (confidence) │ Rationale                                                                                                   │
├──────────────────────────┼────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Architecture Coherence   │     9/10 (95%)     │ Gemini demonstrated strong architectural foresight by proactively identifying potential weaknesses in the   │
│                          │                    │ user's initial design, such as brittle parsers and the need for structured outputs. It then proposed a      │
│                          │                    │ robust 'Hybrid Tiered Strategy' for model selection and a resilient `GeminiEvaluator` design, ensuring the  │
│                          │                    │ tool's long-term stability and reliability.                                                                 │
│ Context Provisioning     │     9/10 (98%)     │ Gemini consistently provided clear and relevant context for the issues encountered and the solutions        │
│                          │                    │ proposed. It explained the '2026 deprecation cycle' for API versioning, the SDK's behavior regarding API    │
│                          │                    │ keys, and the rationale behind architectural decisions like avoiding '-latest' aliases for evaluation       │
│                          │                    │ tools. It also guided the user on how to enforce context in their own evaluation schema.                    │
│ Iterative Reasoning      │     9/10 (95%)     │ Gemini demonstrated excellent iterative reasoning by adapting its solutions based on user feedback. When    │
│                          │                    │ the initial script failed due to an incorrect environment variable assumption, Gemini quickly understood    │
│                          │                    │ the problem and provided a corrected, more robust snippet.                                                  │
│ Hallucination Correction │     9/10 (90%)     │ Gemini proactively addressed the risk of hallucination in the context of the user's evaluation tool. It     │
│                          │                    │ highlighted the importance of 'evidence' fields to prevent the model from 'hallucinating foresight' or      │
│                          │                    │ 'good architecture' and explicitly designed the schema to enforce grounding in transcript text.             │
│ Tooling Coordination     │    10/10 (99%)     │ Gemini provided precise and executable Python code snippets for interacting with the `google-genai` SDK,    │
│                          │                    │ including model listing, API key handling, and configuring thinking parameters. Its understanding of the    │
│                          │                    │ SDK's nuances and versioning changes was exemplary, directly solving the user's technical roadblocks.       │
╰──────────────────────────┴────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────────────────────────────── Timeline Phases ──────────────────────────────────────────────────────────────────────╮
│ Timeline Phases                                                                                                                                             │
│ ├── Initial Architecture Review & Problem Identification 9/10 (95% confidence)                                                                              │
│ │   ├── Highlights                                                                                                                                          │
│ │   │   ├── Proactive identification of brittle parsers                                                                                                     │
│ │   │   ├── Questioning context-anchoring definition                                                                                                        │
│ │   │   └── Suggesting strict JSON schema enforcement                                                                                                       │
│ │   └── Concerns                                                                                                                                            │
│ ├── API Key & Model Resolution Debugging 9/10 (98% confidence)                                                                                              │
│ │   ├── Highlights                                                                                                                                          │
│ │   │   ├── Accurate diagnosis of API versioning issues                                                                                                     │
│ │   │   ├── Provision of executable diagnostic code                                                                                                         │
│ │   │   └── Correction of environment variable assumption based on user feedback                                                                            │
│ │   └── Concerns                                                                                                                                            │
│ ├── Robust Model Configuration & Evaluator Design 10/10 (97% confidence)                                                                                    │
│ │   ├── Highlights                                                                                                                                          │
│ │   │   ├── Proposing a 'Hybrid Tiered Strategy' for model selection                                                                                        │
│ │   │   ├── Refactoring `config.py` with a `DEFAULT_MODEL_PRIORITY` list                                                                                    │
│ │   │   ├── Implementing `_resolve_model` in `GeminiEvaluator` for lazy resolution and fallback logic                                                       │
│ │   │   └── Providing 'Pro-Tips' for robust setup                                                                                                           │
│ │   └── Concerns                                                                                                                                            │
│ ├── Evidence-Based Evaluation Schema & Thinking Budget 9/10 (96% confidence)                                                                                │
│ │   ├── Highlights                                                                                                                                          │
│ │   │   ├── Refactoring Pydantic schema for evidence-based grading                                                                                          │
│ │   │   ├── Introducing `thought_process` for explicit chain of thought                                                                                     │
│ │   │   ├── Integrating `thinking_budget` for deeper reasoning                                                                                              │
│ │   │   └── Explaining the rationale behind citations and thinking budget                                                                                   │
│ │   └── Concerns                                                                                                                                            │
│ └── Stress-Test Transcript Generation 9/10 (95% confidence)                                                                                                 │
│     ├── Highlights                                                                                                                                          │
│     │   ├── Generation of three distinct edge-case transcripts                                                                                              │
│     │   ├── Accurate formatting as markdown conversations with code blocks                                                                                  │
│     │   └── Transcripts designed to test specific evaluation metrics (Context Provisioning, Architecture Scoping, Iterative Reasoning, Hallucination        │
│     │       Correction, Architectural Foresight, Security Vigilance)                                                                                        │
│     └── Concerns                                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────── Prompt Engineering ─────────────────────────────────────────────────────────────────────╮
│ - System Directive: 9/10 | The initial prompt effectively set the context, introduced the project, and clearly defined Gemini's role as a 'Lead Engineer.'  │
│ This established the desired persona and scope for the entire interaction, leading to highly relevant and proactive guidance.                               │
│ - Debugging Request: 8/10 | The user's debugging prompts were clear in describing the error (`404 NOT_FOUND`, `ValueError`) and the desired output (Python  │
│ snippet, rewrite for specific env var). This allowed Gemini to quickly understand and address the technical roadblocks.                                     │
│ - Architectural Refactoring Request: 9/10 | The user clearly articulated a maintenance burden (hardcoded model) and sought a 'production-ready' solution,   │
│ providing their current `config.py`. This well-defined problem statement enabled Gemini to propose a comprehensive and robust architectural refactoring.    │
│ - Schema Design & Agentic Capability Enhancement: 9/10 | The user's prompt clearly outlined the need for evidence-based grading and inquired about          │
│ 'thinking budget,' demonstrating a good understanding of advanced agentic features. This allowed Gemini to provide highly relevant schema refactorings and  │
│ explain the underlying principles.                                                                                                                          │
│ - Content Generation (Edge Cases): 10/10 | The user's request for edge-case transcripts was exceptionally clear, detailing the desired behavior, goal, and  │
│ specific metrics to test for each case. This precision enabled Gemini to generate highly accurate and relevant stress-test content.                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────── Strengths ─────────────────────────────────────────────────────────────────────────╮
│ - Gemini consistently provided proactive architectural insights and identified potential issues before they became major roadblocks.                        │
│ - Gemini offered clear, actionable, and correct code snippets for debugging and implementing robust solutions.                                              │
│ - Gemini demonstrated strong iterative reasoning, adapting its responses and code based on user feedback and new information.                               │
│ - Gemini effectively explained complex API versioning, SDK behaviors, and architectural patterns in an accessible manner.                                   │
│ - Gemini's ability to generate highly specific and relevant stress-test scenarios showcased a deep understanding of the evaluation tool's purpose and the   │
│ 'Staff-level' criteria.                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────────────────────────────── Recommendations ──────────────────────────────────────────────────────────────────────╮
│ - Continue to leverage Gemini's 'Lead Engineer' persona for architectural guidance and proactive problem identification.                                    │
│ - Implement the 'Hybrid Tiered Strategy' for model selection to ensure the `ai-eval-cli` remains resilient to API changes and model deprecations.           │
│ - Fully integrate the `thought_process` and `evidence` fields into the evaluation workflow to ensure all grading is grounded in transcript text, preventing │
│ 'vibe-checking' and enhancing auditability.                                                                                                                 │
│ - Utilize the `thinking_budget` and `thinking_level` parameters in the `GenerateContentConfig` to enable deeper, 'Staff-level' reasoning during             │
│ evaluations.                                                                                                                                                │
│ - Develop a comprehensive System Prompt that clearly defines 'Staff-level architecture' and other evaluation criteria for the `ai-eval-cli` to ensure       │
│ consistent and accurate grading.                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 🧾 How It Works

- **TranscriptEvaluation schema:** Gemini produces a structured payload that always includes `thought_process`, `overall_score`, `ModelConfig`, plus capability scores, timeline phases, prompt insights, strengths, and recommendations.
- **Phase Scores:** Each timeline phase (Planning, Design, Debugging, etc.) is rated 1-10, annotated with confidence, and anchored to verbatim evidence so staff-level reasoning can be audited.
- **Capability Scores:** Capabilities like Architecture Coherence, Debug Strategy, Retrieval Context, and Safety are scored with rationales and exact quotes/turn IDs for traceability.
- **Prompt Engineering Insights:** Each prompt type includes an effectiveness rating and the verbatim text that was used to steer the agent, ensuring you know exactly how the interaction was guided.

These artifacts let Gemini behave as a Staff AI Systems Engineer, narrating its chain-of-thought, citing evidence, and then emitting the final evaluation top-to-bottom.


## 💡 Reflection: What Makes an AI-Assisted Workflow "Good"?

Building this evaluator highlighted that a "good" AI workflow isn't just about generating functional code—it's about steering the system. The best workflows exhibit **proactive architectural scoping** (addressing security and system design before writing parsers), **tight iteration loops** (swiftly correcting hallucinations using explicit evidence or SDK docs), and **precise context provisioning**. Ultimately, an exceptional AI-assisted engineer treats the LLM like a capable but junior teammate: requiring clear bounds, structured schemas, and firm corrections to produce Staff-level output.