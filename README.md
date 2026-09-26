# Jev exploration

## Setup

```
uv sync
cp .env.sample .env   # add TYPESAFE_API_KEY   (needs the stockfish binary: brew install stockfish)
```

## Jev plays chess

Jev plays chess against stockfish.

### Run

```
uv run jev-plays-chess --state san           --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-san
uv run jev-plays-chess --state ascii         --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-ascii
uv run jev-plays-chess --state fen           --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-fen
uv run jev-plays-chess --state pgn_full      --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-pgn_full
uv run jev-plays-chess --state pgn_windowed  --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-pgn_windowed
uv run jev-plays-chess --state prose_1       --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-prose_1
uv run jev-plays-chess --state json_1        --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-json_1
```

### Results

Jev per-move confidence, one 30-ply game each vs Stockfish (UCI_Elo 1320):

| state | moves | mean | median | min | max |
|---|--:|--:|--:|--:|--:|
| san | 12 | 0.25 | 0.23 | 0.06 | 1.00 |
| ascii | 13 | 0.18 | 0.07 | 0.04 | 1.00 |
| fen | 15 | 0.18 | 0.14 | 0.03 | 0.57 |
| pgn_full | 15 | 0.19 | 0.10 | 0.05 | 0.56 |
| pgn_windowed | 15 | 0.22 | 0.20 | 0.04 | 0.55 |
| prose_1 | 15 | 0.29 | 0.30 | 0.08 | 0.54 |
| json_1 | 15 | 0.26 | 0.23 | 0.08 | 0.79 |

## Jev's world knowledge

Test Jev's general world knowledge by running through the [MMLU](https://huggingface.co/datasets/cais/mmlu) dataset.

### Run

```
uv run jev-knows --run-id mmlu-full --concurrency 12
```

### Results

It took 4:35 to run through the full 14k questions at concurrency level 12.

| category | accuracy | n |
|---|--:|--:|
| STEM | 94.7% | 3014 |
| Social sciences | 93.3% | 3074 |
| Other (business, health, misc.) | 91.7% | 3241 |
| Humanities | 88.4% | 4704 |

| category | subject | n | accuracy | confidence when correct | confidence when wrong |
|---|---|--:|--:|--:|--:|
| STEM | college_physics | 102 | 99% | 0.97 | 0.93 |
| STEM | college_biology | 144 | 99% | 0.99 | 0.89 |
| STEM | college_computer_science | 100 | 98% | 0.94 | 0.64 |
| STEM | high_school_computer_science | 100 | 98% | 0.97 | 0.91 |
| STEM | elementary_mathematics | 377 | 97% | 0.97 | 0.79 |
| STEM | college_mathematics | 100 | 97% | 0.93 | 0.75 |
| STEM | astronomy | 152 | 97% | 0.98 | 0.87 |
| STEM | abstract_algebra | 100 | 96% | 0.95 | 0.94 |
| STEM | high_school_chemistry | 202 | 96% | 0.95 | 0.72 |
| STEM | high_school_biology | 310 | 95% | 0.98 | 0.89 |
| STEM | conceptual_physics | 235 | 95% | 0.95 | 0.71 |
| STEM | high_school_mathematics | 270 | 95% | 0.88 | 0.46 |
| STEM | high_school_physics | 150 | 94% | 0.96 | 0.70 |
| STEM | high_school_statistics | 216 | 94% | 0.93 | 0.72 |
| STEM | computer_security | 100 | 91% | 0.95 | 0.71 |
| STEM | machine_learning | 112 | 90% | 0.93 | 0.70 |
| STEM | electrical_engineering | 144 | 89% | 0.94 | 0.65 |
| STEM | college_chemistry | 100 | 75% | 0.95 | 0.67 |
| Social sciences | high_school_microeconomics | 238 | 99% | 0.98 | 0.47 |
| Social sciences | high_school_government_and_politics | 193 | 98% | 0.99 | 0.55 |
| Social sciences | high_school_psychology | 545 | 97% | 0.98 | 0.71 |
| Social sciences | us_foreign_policy | 100 | 96% | 0.95 | 0.51 |
| Social sciences | high_school_macroeconomics | 389 | 95% | 0.96 | 0.80 |
| Social sciences | high_school_geography | 198 | 94% | 0.97 | 0.87 |
| Social sciences | sociology | 200 | 92% | 0.97 | 0.73 |
| Social sciences | professional_psychology | 612 | 92% | 0.95 | 0.70 |
| Social sciences | human_sexuality | 131 | 92% | 0.92 | 0.57 |
| Social sciences | econometrics | 114 | 86% | 0.94 | 0.70 |
| Social sciences | security_studies | 245 | 84% | 0.86 | 0.65 |
| Social sciences | public_relations | 109 | 81% | 0.90 | 0.62 |
| Other | medical_genetics | 100 | 100% | 0.98 | - |
| Other | miscellaneous | 783 | 97% | 0.97 | 0.69 |
| Other | professional_medicine | 272 | 97% | 0.98 | 0.77 |
| Other | marketing | 234 | 97% | 0.96 | 0.51 |
| Other | clinical_knowledge | 265 | 95% | 0.96 | 0.62 |
| Other | professional_accounting | 282 | 95% | 0.92 | 0.51 |
| Other | nutrition | 306 | 94% | 0.94 | 0.74 |
| Other | management | 103 | 93% | 0.95 | 0.71 |
| Other | anatomy | 135 | 93% | 0.96 | 0.84 |
| Other | college_medicine | 173 | 89% | 0.95 | 0.71 |
| Other | human_aging | 223 | 84% | 0.92 | 0.70 |
| Other | business_ethics | 99 | 84% | 0.93 | 0.39 |
| Other | global_facts | 100 | 74% | 0.81 | 0.60 |
| Other | virology | 166 | 56% | 0.92 | 0.87 |
| Humanities | formal_logic | 126 | 98% | 0.93 | 0.76 |
| Humanities | high_school_world_history | 237 | 96% | 0.98 | 0.60 |
| Humanities | high_school_us_history | 204 | 95% | 0.98 | 0.74 |
| Humanities | world_religions | 171 | 94% | 0.96 | 0.73 |
| Humanities | international_law | 120 | 93% | 0.97 | 0.66 |
| Humanities | prehistory | 324 | 93% | 0.94 | 0.62 |
| Humanities | logical_fallacies | 163 | 93% | 0.96 | 0.76 |
| Humanities | philosophy | 311 | 93% | 0.92 | 0.64 |
| Humanities | jurisprudence | 108 | 92% | 0.96 | 0.70 |
| Humanities | high_school_european_history | 165 | 91% | 0.97 | 0.84 |
| Humanities | moral_disputes | 346 | 85% | 0.91 | 0.71 |
| Humanities | professional_law | 1534 | 85% | 0.85 | 0.64 |
| Humanities | moral_scenarios | 895 | 84% | 0.86 | 0.60 |

## Prompt routing

Route customer queries to intents using [banking77](https://huggingface.co/datasets/mteb/banking77).

### Run

```
uv run jev-routes --run-id routing-full --concurrency 12
```

### Results

It took 0:58 to route all 3076 queries at concurrency level 12.

| correct | confidence when right | confidence when wrong |
|--:|--:|--:|
| 79.2% | 0.92 | 0.70 |

## Compliance

Classify statements against a legal rule using [LegalBench](https://huggingface.co/datasets/nguha/legalbench). The task's rule is supplied in the instruction (the `hearsay` task shown here).

### Run

```
uv run jev-complies --task hearsay --run-id hearsay-full --concurrency 12
```

### Results

It took 0:03 to classify all 94 statements at concurrency level 12.

76.6% correct (72/94). Confidence averaged 0.66 on correct answers, 0.40 on wrong.

| slice | n | accuracy |
|---|--:|--:|
| Non-assertive conduct | 19 | 100% |
| Statement made in-court | 14 | 100% |
| Not introduced to prove truth | 20 | 85% |
| Standard hearsay | 29 | 66% |
| Non-verbal hearsay | 12 | 25% |

## Judging game levels

Rubrics from [autoregressive-schemas](https://github.com/jdhornsby/autoregressive-schemas), copied into `data/autoregressive_schemas/`. The rubric is 0-indexed for jev and 1-5 for the original judge, so scores are shifted to align but are not apples-to-apples.

### Run

```
uv run jev-judges --condition minimal --run-id judge-full
```

### Results

384 levels, `minimal` thinking, run `judge-full-01`.

Schema-variant scores (weighted likert, and reachability break %):

| variant | original | jev | original break % | jev break % |
|---|--:|--:|--:|--:|
| flat_alpha | 3.84 | 4.46 | 5.2 | 3.6 |
| alpha_nested | 3.84 | 4.47 | 4.2 | 2.6 |
| ui_contract | 3.89 | 4.56 | 1.0 | 1.0 |
| append_order | 4.18 | 4.55 | 8.9 | 7.8 |
| grouped_by_type | 4.18 | 4.62 | 1.6 | 1.0 |
| nested_narrative | 4.32 | 4.64 | 0.0 | 0.0 |

Per criterion - means, spread, rank agreement:

| criterion | original | jev | original SD | jev SD | Spearman |
|---|--:|--:|--:|--:|--:|
| reference_integrity | 3.90 | 4.53 | 1.14 | 0.54 | 0.68 |
| causal_chain | 3.85 | 4.60 | 1.19 | 0.38 | 0.48 |
| balance | 4.12 | 4.33 | 1.00 | 0.20 | 0.41 |
| thematic_coherence | 4.50 | 4.68 | 0.68 | 0.24 | 0.35 |
| mechanical_sense | 3.91 | 4.40 | 0.90 | 0.49 | 0.34 |
| completeness | 4.10 | 4.81 | 0.88 | 0.09 | 0.40 |
| weighted | 4.04 | 4.55 | 0.59 | 0.20 | 0.58 |

Reachability differences (11 of 13 disagreements, where jev read reachable but the original broke it):

| category | verdict | jev confidence | n |
|---|---|--:|--:|
| semantic match | jev more accurate — Haiku missed it reading literally | 0.71–0.96 | 6 |
| plausible inference | debatable | 0.60–0.83 | 3 |
| semantic overreach | Haiku more accurate — jev too generous | 0.50–0.67 | 2 |

Other metrics:

| metric | value |
|---|--:|
| reachability agreement | 1139/1152 = 98.9% |
| jev confidence, agreements | 0.89 |
| jev confidence, disagreements | 0.49 |
| per-item scores identical across 10 runs | 0/2304 |
| per-item score range across 10 runs, mean / max | 0.11 / 1.06 |
| variant-mean range across 10 runs | ≤0.006 |
| latency per call, median / p95 | 0.23s / 0.38s |
| retries | 0/3840 |

## Tokenizer fingerprinting

Builds a set of sample strings via search optimized to discriminate between a set of candidate tokenizers then measures Jev's similarity to them

```
uv run --group fingerprint jev-tokenizer
```

### Sample stats

`seed 0  samples 200  pairs 91  coverage 1818`

| candidate | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0 cl100k | – | 66 | 167 | 67 | 189 | 188 | 127 | 87 | 376 | 125 | 443 | 426 | 43 | 85 |
| 1 o200k | 66 | – | 109 | 59 | 202 | 196 | 137 | 38 | 334 | 125 | 426 | 412 | 73 | 85 |
| 2 Qwen3 | 167 | 109 | – | 164 | 305 | 289 | 124 | 104 | 251 | 169 | 348 | 332 | 179 | 109 |
| 3 Llama3 | 67 | 59 | 164 | – | 190 | 189 | 126 | 66 | 375 | 125 | 426 | 410 | 65 | 85 |
| 4 Llama2 | 189 | 202 | 305 | 190 | – | 21 | 265 | 209 | 512 | 146 | 485 | 469 | 155 | 202 |
| 5 Mistral | 188 | 196 | 289 | 189 | 21 | – | 259 | 200 | 509 | 137 | 479 | 463 | 151 | 196 |
| 6 Gemma2 | 127 | 137 | 124 | 126 | 265 | 259 | – | 109 | 344 | 129 | 441 | 431 | 139 | 135 |
| 7 DeepSeek | 87 | 38 | 104 | 66 | 209 | 200 | 109 | – | 327 | 133 | 419 | 407 | 88 | 85 |
| 8 BERT | 376 | 334 | 251 | 375 | 512 | 509 | 344 | 327 | – | 377 | 108 | 95 | 383 | 334 |
| 9 RoBERTa | 125 | 125 | 169 | 125 | 146 | 137 | 129 | 133 | 377 | – | 455 | 440 | 121 | 125 |
| 10 DeBERTa3 | 443 | 426 | 348 | 426 | 485 | 479 | 441 | 419 | 108 | 455 | – | 51 | 448 | 426 |
| 11 XLM-R | 426 | 412 | 332 | 410 | 469 | 463 | 431 | 407 | 95 | 440 | 51 | – | 431 | 412 |
| 12 ModernBERT | 43 | 73 | 179 | 65 | 155 | 151 | 139 | 88 | 383 | 121 | 448 | 431 | – | 77 |
| 13 o200k-qwenpre | 85 | 85 | 109 | 85 | 202 | 196 | 135 | 85 | 334 | 125 | 426 | 412 | 77 | – |

### Results

| candidate | ascii(17) | cjk(43) | contract(14) | digits(10) | emoji(59) | other(46) | space(10) |
|---|--:|--:|--:|--:|--:|--:|--:|
| o200k-qwenpre | 0.94 | 0.98 | 0.86 | 1.00 | 0.53 | 0.72 | 0.80 |
| o200k | 0.94 | 0.98 | 0.64 | 0.00 | 0.53 | 0.72 | 0.80 |
| Llama3 | 0.65 | 0.47 | 0.07 | 0.00 | 0.07 | 0.41 | 0.80 |
| DeepSeek | 0.35 | 0.09 | 0.00 | 0.00 | 0.10 | 0.41 | 0.50 |
| cl100k | 0.47 | 0.05 | 0.07 | 0.00 | 0.05 | 0.22 | 0.80 |
| Gemma2 | 0.18 | 0.12 | 0.00 | 1.00 | 0.00 | 0.17 | 0.40 |
| Qwen3 | 0.41 | 0.05 | 0.07 | 1.00 | 0.00 | 0.00 | 0.80 |
| ModernBERT | 0.18 | 0.05 | 0.00 | 0.00 | 0.03 | 0.07 | 0.30 |
| RoBERTa | 0.12 | 0.00 | 0.00 | 0.00 | 0.05 | 0.09 | 0.00 |
| Llama2 | 0.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 |
| Mistral | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.10 |
| DeBERTa3 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| XLM-R | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| BERT | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
