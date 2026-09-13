"""Tiny, dependency-free metric example for the 50 sanity forms.

This is deliberately a character tokenizer: every Unicode code point is one token.
It makes offsets and all benchmark metrics easy to inspect. It is a baseline, not an
LLM tokenizer. Run from this directory with:

    python example_50_character_baseline.py
"""
from __future__ import annotations

import ast
import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "data" / "SlovakTokenBench_v1.csv"


def character_tokenize(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    return list(text), [(i, i + 1) for i in range(len(text))]


def boundaries(offsets: list[tuple[int, int]], text_len: int) -> set[int]:
    return {end for _, end in offsets if 0 < end < text_len}


def crossing_count(offsets: list[tuple[int, int]], gold: set[int]) -> int:
    return sum(any(start < boundary < end for start, end in offsets) for boundary in gold)


def boundary_metrics(predicted: set[int], gold: set[int]) -> tuple[float | None, float | None, float | None]:
    if not gold:
        return None, None, None
    true_positive = len(predicted & gold)
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(gold)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate(row: dict[str, str]) -> dict[str, float | int | None]:
    form = row["form"]
    tokens, offsets = character_tokenize(form)
    gold = set(ast.literal_eval(row["stem_suffix_boundary"]))
    predicted = boundaries(offsets, len(form))
    crossed = crossing_count(offsets, gold)
    mbcr = crossed / len(gold) if gold else None
    precision, recall, f1 = boundary_metrics(predicted, gold)
    return {
        "token_count": len(tokens),
        "fertility": len(tokens) / len(form) if form else None,
        "strict_stem_boundary_match": int(bool(gold) and gold.issubset(predicted)) if gold else None,
        "morpheme_boundary_crossing_rate": mbcr,
        "morphological_alignment_score": 1.0 - mbcr if mbcr is not None else None,
        "boundary_precision": precision,
        "boundary_recall": recall,
        "boundary_f1": f1,
    }


def mean(rows: list[dict], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row[key] is not None]
    return sum(values) / len(values) if values else None


def main() -> None:
    with INPUT.open(encoding="utf-8", newline="") as handle:
        # The public release contains one CSV.  Keep the 50 sanity forms out
        # of the scored benchmark by selecting them by split here.
        data = [row for row in csv.DictReader(handle) if row["split"] == "simple_examples"]
    if len(data) != 50:
        raise RuntimeError(f"Expected 50 simple_examples, found {len(data)}")
    results = [evaluate(row) for row in data]
    print(f"forms={len(results)} tokenizer=character (one Unicode code point per token)")
    for key in (
        "token_count", "fertility", "strict_stem_boundary_match",
        "morpheme_boundary_crossing_rate", "morphological_alignment_score",
        "boundary_precision", "boundary_recall", "boundary_f1",
    ):
        value = mean(results, key)
        print(f"{key}={value:.6f}" if value is not None else f"{key}=NA")


if __name__ == "__main__":
    main()
