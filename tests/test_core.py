"""Tests for FIDELIO scoring and report rendering."""

from __future__ import annotations

import pytest

from fidelio.core import Question, evaluate, render_markdown, render_text
from fidelio.questions import CATEGORIES, QUESTIONS

PERFECT = {q.id: 0 for q in QUESTIONS}
PERFECTLY_BAD = {q.id: len(q.choices) - 1 for q in QUESTIONS}


def test_question_bank_is_well_formed() -> None:
    ids = [q.id for q in QUESTIONS]
    assert len(ids) == len(set(ids)), "question ids must be unique"
    for question in QUESTIONS:
        assert question.category in {c.key for c in CATEGORIES}


def test_evaluate_counts_answered_and_raw() -> None:
    answers = {QUESTIONS[0].id: 3}
    result = evaluate(answers, CATEGORIES, QUESTIONS)
    section = result.scores["accounts"]
    assert section.answered == 1
    assert section.raw == 3
    assert section.max_raw > 0
    assert section.score == pytest.approx(round(100 * 3 / section.max_raw))


def test_perfect_answers_score_zero() -> None:
    result = evaluate(PERFECT, CATEGORIES, QUESTIONS)
    assert result.overall == 0
    assert all(score.score == 0 for score in result.scores.values())
    assert result.unanswered == []


def test_terrible_answers_score_full() -> None:
    result = evaluate(PERFECTLY_BAD, CATEGORIES, QUESTIONS)
    assert result.overall == 100
    assert all(score.score == 100 for score in result.scores.values())


def test_unanswered_questions_are_reported() -> None:
    answers = dict(PERFECT)
    answers.pop(QUESTIONS[0].id)
    result = evaluate(answers, CATEGORIES, QUESTIONS)
    assert result.unanswered == [QUESTIONS[0].id]


def test_out_of_range_choice_raises() -> None:
    with pytest.raises(ValueError):
        evaluate({QUESTIONS[0].id: 99}, CATEGORIES, QUESTIONS)


def test_weight_override_changes_overall_only() -> None:
    bad = {QUESTIONS[0].id: len(QUESTIONS[0].choices) - 1}
    result = evaluate(bad, CATEGORIES, QUESTIONS, weights={"accounts": 2.0})
    section = result.scores["accounts"]
    assert section.weight == 2.0
    # the per-category score is unaffected by weight; overall folds it in
    assert evaluate(bad, CATEGORIES, QUESTIONS).overall != result.overall


def test_question_declaration_requires_alignment() -> None:
    with pytest.raises(ValueError):
        Question("bad", "accounts", "t", ("a", "b"), (0, 1, 2))
    with pytest.raises(ValueError):
        Question("bad", "accounts", "t", (), ())


def test_render_text_contains_scores_and_overall() -> None:
    text = render_text(evaluate(PERFECT, CATEGORIES, QUESTIONS), QUESTIONS)
    assert "Overall" in text
    assert "100" in text or "0" in text


def test_render_markdown_contains_next_steps() -> None:
    md = render_markdown(evaluate(PERFECT, CATEGORIES, QUESTIONS), QUESTIONS)
    assert "FIDELIO — remediation roadmap" in md
    assert "next step" in md
    assert "never proof of anonymity" in md
