from __future__ import annotations

from statistics import mean
from typing import Iterable, Sequence

from rich import box
from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ..schema.evaluation import (
    CapabilityScore,
    PhaseScore,
    PromptEngineeringInsight,
    TranscriptEvaluation,
)


def color_for_score(score: float) -> str:
    if score >= 8:
        return "bold green"
    if score >= 5:
        return "bold yellow"
    return "bold red"


def render_single(console: Console, evaluation: TranscriptEvaluation) -> None:
    console.print(Rule(f"[bold cyan]Transcript: {evaluation.transcript_id}"))

    overall_panel = Panel(
        Text(
            f"{evaluation.overall_score}/10",
            style=color_for_score(evaluation.overall_score),
            justify="center",
        ),
        title="Overall Score",
        subtitle="Staff-level effectiveness",
        border_style=color_for_score(evaluation.overall_score),
    )

    capability_table = _build_capability_table(evaluation.capability_scores)
    timeline_tree = _build_timeline_tree(evaluation.timeline_phases)
    prompt_panel = _build_prompt_panel(evaluation.prompt_engineering)
    strengths_panel = Panel(
        "\n".join(f"- {s}" for s in evaluation.strengths) or "None noted",
        title="Strengths",
        border_style="green",
    )
    recommendations_panel = Panel(
        "\n".join(f"- {r}" for r in evaluation.recommendations) or "None noted",
        title="Recommendations",
        border_style="yellow",
    )

    console.print(overall_panel)
    console.print(Columns([capability_table, Panel(timeline_tree, title="Timeline Phases")]))
    console.print(Columns([prompt_panel, strengths_panel, recommendations_panel]))


def render_comparison(console: Console, evaluations: Sequence[TranscriptEvaluation]) -> None:
    console.print(Rule("[bold magenta]Comparative View"))
    table = Table(title="Transcript Comparison", box=box.SIMPLE_HEAVY)
    table.add_column("Metric", justify="left")

    for eval in evaluations:
        table.add_column(eval.transcript_id, justify="center")

    table.add_row(
        "Overall Score",
        *[
            Text(f"{eval.overall_score}/10", style=color_for_score(eval.overall_score))
            for eval in evaluations
        ],
    )

    table.add_row(
        "Avg Capability",
        *[
            Text(
                f"{mean([cap.score for cap in eval.capability_scores]):.1f}",
                style=color_for_score(mean([cap.score for cap in eval.capability_scores])),
            )
            for eval in evaluations
        ],
    )

    table.add_row(
        "Total Strengths",
        *[str(len(eval.strengths)) for eval in evaluations],
    )

    console.print(table)


def _build_capability_table(capabilities: Iterable[CapabilityScore]) -> Table:
    table = Table(title="Capability Scores", box=box.ROUNDED, expand=True)
    table.add_column("Metric")
    table.add_column("Score (confidence)", justify="center")
    table.add_column("Rationale", justify="left", overflow="fold")

    for cap in capabilities:
        score_text = Text(
            f"{cap.score}/10 ({cap.confidence_score:.0f}%)",
            style=color_for_score(cap.score),
        )
        table.add_row(cap.metric, score_text, cap.rationale)

    return table


def _build_timeline_tree(phases: Sequence[PhaseScore]) -> Tree:
    tree = Tree("Timeline Phases")
    for phase in phases:
        branch = tree.add(
            f"{phase.name} [bold]{phase.score}/10[/] ({phase.confidence_score:.0f}% confidence)"
        )
        highlights_branch = branch.add("[bold]Highlights[/]")
        for highlight in phase.highlights:
            highlights_branch.add(highlight)
        concerns_branch = branch.add("[bold]Concerns[/]")
        for concern in phase.concerns:
            concerns_branch.add(concern)
    return tree


def _build_prompt_panel(prompts: Iterable[PromptEngineeringInsight]) -> Panel:
    panel = Panel(
        "\n".join(
            f"- {insight.prompt_type}: {insight.effectiveness}/10 | {insight.rationale}"
            for insight in prompts
        )
        or "No prompt insights captured.",
        title="Prompt Engineering",
        border_style="blue",
    )
    return panel
