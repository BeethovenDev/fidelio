"""Scoring, weighting and report rendering for FIDELIO.

The maths is deliberately simple and transparent: every answer carries a risk
0..3, a category score is ``100 * raw / max_raw``, and an optional per-category
``weight`` folds into the overall score. Nothing is hidden behind a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "AuditResult",
    "Category",
    "CategoryScore",
    "Question",
    "evaluate",
    "render_markdown",
    "render_text",
]

_MAX_RISK = 3


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    blurb: str


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    text: str
    choices: tuple[str, ...]
    risks: tuple[int, ...]
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.choices) != len(self.risks):
            raise ValueError(f"{self.id}: choices and risks must be aligned")
        if not self.choices:
            raise ValueError(f"{self.id}: at least one choice required")
        if any(not 0 <= r <= _MAX_RISK for r in self.risks):
            raise ValueError(f"{self.id}: risks must be within 0..{_MAX_RISK}")


@dataclass
class CategoryScore:
    category: Category
    raw: int = 0
    max_raw: int = 0
    answered: int = 0
    weight: float = 1.0
    selections: list[tuple[str, str]] = field(default_factory=list)  # (question_id, choice)

    @property
    def score(self) -> int:
        """0 does not improve with ``weight``; weights fold in at the overall level."""
        if self.max_raw == 0:
            return 0
        return min(100, max(0, round(100 * self.raw / self.max_raw)))


@dataclass
class AuditResult:
    scores: dict[str, CategoryScore]
    unanswered: list[str]
    weight_overrides: dict[str, float]

    @property
    def overall(self) -> int:
        weighted = sum(s.score * s.weight for s in self.scores.values())
        total_weight = sum(s.weight for s in self.scores.values())
        return round(weighted / total_weight) if total_weight else 0

    def to_dict(self) -> dict[str, object]:
        return {
            "overall": self.overall,
            "scores": {
                key: {
                    "score": s.score,
                    "raw": s.raw,
                    "max_raw": s.max_raw,
                    "answered": s.answered,
                    "weight": s.weight,
                }
                for key, s in sorted(self.scores.items())
            },
            "unanswered": sorted(self.unanswered),
        }


def evaluate(
    answers: dict[str, int],
    categories: tuple[Category, ...],
    questions: tuple[Question, ...],
    weights: dict[str, float] | None = None,
) -> AuditResult:
    """Score ``answers`` (question id -> chosen index) against the bank."""
    scores = {category.key: CategoryScore(category) for category in categories}
    for question in questions:
        section = scores[question.category]
        section.max_raw += max(question.risks)
        if question.id not in answers:
            continue
        index = answers[question.id]
        if not 0 <= index < len(question.choices):
            raise ValueError(f"{question.id}: choice {index} out of range")
        section.raw += question.risks[index]
        section.answered += 1
        section.selections.append((question.id, question.choices[index]))

    overrides = dict(weights or {})
    for key, weight in overrides.items():
        if key in scores and weight >= 0:
            scores[key].weight = weight

    unanswered = [q.id for q in questions if q.id not in answers]
    return AuditResult(scores, unanswered, overrides)


def _bar(score: int) -> str:
    filled = round(score / 100 * 20)
    return "#" * filled + "-" * (20 - filled)


def render_text(result: AuditResult, questions: tuple[Question, ...]) -> str:
    by_category: dict[str, list[Question]] = {key: [] for key in result.scores}
    for question in questions:
        by_category[question.category].append(question)

    lines = ["OPSEC self-audit — scores (0 = tight, 100 = loud)\n"]
    for category in result.scores.values():
        count = len(by_category[category.category.key])
        lines.append(
            f"{category.category.title:<24} "
            f"{category.score:>3}/100  [{_bar(category.score)}]  "
            f"{category.answered}/{count} answered"
        )
    lines.append(f"{'Overall':<24} {result.overall:>3}/100")
    if result.unanswered:
        lines.append(f"\nleft unanswered: {', '.join(sorted(result.unanswered))}")
    lines.append("\nscores measure habits, never proof of anonymity.")
    return "\n".join(lines)


def render_markdown(result: AuditResult, questions: tuple[Question, ...]) -> str:
    by_category: dict[str, list[Question]] = {}
    for question in questions:
        by_category.setdefault(question.category, []).append(question)

    out = [
        "# FIDELIO — remediation roadmap",
        "",
        f"Overall exposure: **{result.overall}/100**",
        "",
    ]
    order = [s.category for _, s in sorted(result.scores.items(), key=lambda kv: kv[0])]
    for category in order:
        section = result.scores[category.key]
        out.append(f"## {category.title}")
        out.append(f"`{category.blurb}`")
        out.append("")
        out.append(f"- score: **{section.score}/100** · answered "
                   f"{section.answered}/{len(by_category.get(category.key, []))}")
        out.append("")
        for question in by_category.get(category.key, []):
            chosen = next(
                (choice for qid, choice in section.selections if qid == question.id),
                None,
            )
            out.append(f"### {question.id} — {question.text}")
            out.append("")
            if chosen is not None:
                out.append(f"- you answered: *{chosen}*")
            else:
                out.append("- *left unanswered*")
            out.append(f"- **next step:** {question.note}")
            out.append("")
    out.append("---")
    out.append("")
    out.append("> Scores measure habits, never proof of anonymity.")
    return "\n".join(out)


def audit_to_dict(result: AuditResult, questions: tuple[Question, ...]) -> dict[str, object]:
    payload = result.to_dict()
    payload["questions"] = {
        question.id: {
            "category": question.category,
            "note": question.note,
        }
        for question in questions
    }
    return payload
