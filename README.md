# SlovakTokenBench

SlovakTokenBench is a compact benchmark for evaluating how subword tokenizers process Slovak noun forms. It reports both compression and preservation of the reference stem--suffix boundary.

This repository contains the benchmark data, the paper, the published summary results, and one dependency-free example that demonstrates every metric.

## Repository contents

```text
.
├── README.md
├── code/
│   └── example_50_character_baseline.py
├── data/
│   └── SlovakTokenBench_v1.csv
└── paper/
    └── Evaluating_Tokenization_Mismatch_in_Slovak_Morphology.pdf
```

## Dataset

The CSV contains 1,050 rows: 1,000 scored forms and 50 separate `simple_examples`. The proportions include 330 random general forms for broad coverage, 270 pattern-representative forms cover the 27 most common declension patterns, 300 hard cases which should stress tokenization on long or unusual words, and 100 morphological-edge cases which target alternations and short endings.

| Split | Rows |
|---|---:|
| `simple_examples` | 50 |
| `random_general` | 330 |
| `pattern_representative` | 270 |
| `hard_tokenization` | 300 |
| `morphological_edge` | 100 |

The manually corrected `form` column is authoritative. `stem`, `suffix`, and `stem_suffix_boundary` are derived from that surface form. The source morphemes and lemma metadata come from the Slovak Root Morpheme Dictionary. The JÚĽŠ noun database is the external inflection reference: <https://slovnik.juls.savba.sk/>.

## Metrics

- `token_count`: number of tokens emitted for a form.
- `fertility`: `token_count / character_count`; lower is more compact.
- `strict_stem_boundary_match`: 1 only when every reference boundary is an exact token boundary.
- `morpheme_boundary_crossing_rate` (MBCR): fraction of reference boundaries crossed inside a token; lower is better.
- `morphological_alignment_score`: `1 - MBCR`; higher is better.
- `boundary_precision`, `boundary_recall`, `boundary_f1`: set comparison between predicted token boundaries and reference boundaries.

Rows with a zero suffix have no internal gold boundary. They remain included for token-count and fertility means and are excluded from boundary-rate means.

## How the evaluator works

The research evaluator performs the following steps:

1. Reads the benchmark CSV and selects the scored rows (or all rows when the examples flag is enabled).
2. Loads each tokenizer adapter from the tokenizer registry.
3. Tokenizes every surface form and converts token spans to Unicode character offsets. Byte-level tokenizers are aligned safely to code-point boundaries.
4. Compares predicted token boundaries with the reference stem--suffix boundary.
5. Computes the metrics above for every row and writes aggregate summaries by
   tokenizer, split, case, suffix, and declension pattern.

The published summary is `results/benchmark_tokenizer_summary.csv`. A full local run produces the same summary together with form-level detail files. The evaluator prints progress such as:

```text
Loading openai_o200k_base (o200k_base)...
  OK: openai_o200k_base
Evaluating openai_o200k_base on 1000 benchmark forms...
Wrote benchmark_tokenization_metrics.csv
Wrote benchmark_tokenizer_summary.csv
```

The dependency-free example below is the runnable demonstration.

## Example

Run:

```bash
python -X utf8 code/example_50_character_baseline.py
```

It reads the 50 `simple_examples` and prints all metrics. Its expected output is:

```text
forms=50 tokenizer=character (one Unicode code point per token)
token_count=6.400000
fertility=1.000000
strict_stem_boundary_match=1.000000
morpheme_boundary_crossing_rate=0.000000
morphological_alignment_score=1.000000
boundary_precision=0.190149
boundary_recall=1.000000
boundary_f1=0.316508
```

This character baseline is only a transparent metric demonstration; it is not intended as a claim that character tokenization is optimal.

## Published results

The summary CSV contains the numeric results used in the paper **Evaluating Tokenization Mismatch in Slovak Morphology**. The main comparison shows that `openai_cl100k_base` has the lowest MBCR (0.502), while `slovakbert` has the lowest fertility (0.357) and the highest MBCR (0.874).
