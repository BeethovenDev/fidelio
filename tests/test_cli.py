"""CLI-level tests for FIDELIO."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fidelio.questions import QUESTIONS


def _run(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "fidelio", *argv],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_list_questions_json_is_stable(tmp_path: Path) -> None:
    proc = _run("--json", "list-questions", cwd=tmp_path)
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert len(payload["questions"]) == len(QUESTIONS)
    assert all("risks" in q for q in payload["questions"])


def test_audit_with_answers_scores_and_exits_zero(tmp_path: Path) -> None:
    answers = {q.id: 0 for q in QUESTIONS}
    answers_file = tmp_path / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    proc = _run("--json", "audit", "--answers", str(answers_file), cwd=tmp_path)
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["overall"] == 0
    assert payload["unanswered"] == []


def test_audit_bad_answers_are_rejected(tmp_path: Path) -> None:
    answers_file = tmp_path / "answers.json"
    answers_file.write_text(json.dumps({"acct_01": 99}), encoding="utf-8")
    proc = _run("audit", "--answers", str(answers_file), cwd=tmp_path)
    assert proc.returncode == 1
    assert "out of range" in proc.stderr


def test_audit_report_file_is_written(tmp_path: Path) -> None:
    answers = {q.id: len(q.choices) - 1 for q in QUESTIONS}
    answers_file = tmp_path / "answers.json"
    answers_file.write_text(json.dumps(answers), encoding="utf-8")
    report = tmp_path / "roadmap.md"
    proc = _run("audit", "--answers", str(answers_file), "--report", str(report),
                cwd=tmp_path)
    assert proc.returncode == 0
    assert "# FIDELIO — remediation roadmap" in report.read_text(encoding="utf-8")
