"""FIDELIO command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fidelio import BANNER, __version__
from fidelio.core import (
    evaluate,
    render_markdown,
    render_text,
)
from fidelio.questions import CATEGORIES, QUESTIONS

__all__ = ["main"]


def _emit_json(payload: object) -> None:
    print(json.dumps(payload, indent=2))


def _load_answers(path: str | None) -> dict[str, int]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--answers must be a JSON object mapping question id to choice index")
    answers: dict[str, int] = {}
    for key, value in data.items():
        if not isinstance(value, int):
            raise ValueError(f"--answers: value for {key!r} must be an integer")
        answers[key] = value
    return answers


def _load_weights(path: str | None) -> dict[str, float] | None:
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--weights must be a JSON object mapping category key to weight")
    return {key: float(value) for key, value in data.items()}


def _prompt(question: object) -> int:
    from fidelio.core import Question

    assert isinstance(question, Question)
    print(f"\n{question.id} [{question.category}] · {question.text}")
    for index, (choice, risk) in enumerate(zip(question.choices, question.risks, strict=True)):
        marker = "!" if risk >= 2 else " "
        print(f"  [{index}] {choice}  {marker}")
    while True:
        try:
            raw = input("choose [0..n] / s to skip: ").strip()
        except (EOFError, KeyboardInterrupt):
            return -1
        if raw.lower() in {"s", "skip"}:
            return -1
        if raw.isdigit() and 0 <= int(raw) < len(question.choices):
            return int(raw)


def cmd_audit(args: argparse.Namespace) -> int:
    answers = _load_answers(args.answers)
    weights = _load_weights(args.weights)

    if not args.answers:
        for question in QUESTIONS:
            choice = _prompt(question)
            if choice >= 0:
                answers[question.id] = choice

    try:
        result = evaluate(answers, CATEGORIES, QUESTIONS, weights)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.report:
        Path(args.report).write_text(
            render_markdown(result, QUESTIONS), encoding="utf-8"
        )
        print(f"roadmap written to {args.report}", file=sys.stderr)

    if args.json:
        payload = result.to_dict()
        payload["questions_bank"] = len(QUESTIONS)
        _emit_json(payload)
    else:
        print(render_text(result, QUESTIONS))
    return 0


def cmd_list_questions(args: argparse.Namespace) -> int:
    if args.json:
        _emit_json(
            {
                "categories": [
                    {"key": c.key, "title": c.title, "blurb": c.blurb}
                    for c in CATEGORIES
                ],
                "questions": [
                    {
                        "id": q.id,
                        "category": q.category,
                        "text": q.text,
                        "choices": list(q.choices),
                        "risks": list(q.risks),
                        "note": q.note,
                    }
                    for q in QUESTIONS
                ],
            }
        )
        return 0
    for category in CATEGORIES:
        print(f"## {category.title} — {category.blurb}")
        for question in QUESTIONS:
            if question.category != category.key:
                continue
            print(f"\n{question.id}: {question.text}")
            for index, choice in enumerate(question.choices):
                print(f"   {index}. {choice}")
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fidelio",
        description="Offline OPSEC / digital-footprint self-audit — Beethoven's Fidelio.",
        epilog="Repo: https://github.com/BeethovenDev/fidelio",
    )
    parser.add_argument("--version", action="version", version=f"fidelio {__version__}")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="run the self-audit")
    p_audit.add_argument("--answers", metavar="ANSWERS.json",
                         help="pre-filled answers ({question_id: choice_index})")
    p_audit.add_argument("--weights", metavar="WEIGHTS.json",
                         help="per-category weight overrides ({category: 0..n})")
    p_audit.add_argument("--report", metavar="PATH.md",
                         help="write a remediation roadmap to a markdown file")
    p_audit.set_defaults(func=cmd_audit)

    p_list = sub.add_parser("list-questions", help="print the question taxonomy")
    p_list.set_defaults(func=cmd_list_questions)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    print(BANNER, file=sys.stderr)
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
