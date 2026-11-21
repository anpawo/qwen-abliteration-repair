# Repairing an abliterated Qwen3.5-9B by restoring weights

**Result: the repaired model scores 65/74 on the dev set and 68/74 on the held-out set (original Qwen3.5-9B at Q3_K_S: 57/74), 87.3% on a 150-problem MATH-500 sample, and refuses 0 of 6 harmful prompts, in a 5.6 GB Q4_K_M that runs on a 4 GB GPU with 8 GB of RAM. Against the two Heretic builds of the same size on the same tests, it ties the best one on MATH-500 (131/150 each) and leads it on the held-out set (68 vs 60).**

Weights (GGUF, with an Ollama Modelfile): https://huggingface.co/anpawo/Qwen3.5-9B-abliterated-repaired-GGUF

An abliterated model (its refusal direction removed from the weights) answers everything, but abliteration also costs
it reasoning. This project copies part of the original weights back into the abliterated model, so that it regains
its reasoning while still not refusing, and then rebuilds the result at the highest precision that fits a small GPU.

Everything here ran on one Windows PC with 4.3 GB of usable VRAM and 8 GB of RAM. A model has to fit in about 5.6 GB,
and that limit drove every choice.

## Result

`H_8-15.Q4_K_M.im`: the abliterated model with every tensor that abliteration changed in layers 8-15 restored from the
original, rebuilt from f16 at Q4_K_M with an importance matrix.

| Model | Dev set (74) | Held-out set (74) | Refusals (6 prompts) |
|---|---|---|---|
| Original Qwen3.5-9B, Q3_K_S | 57 | | 6/6 |
| H_8-15, Q3_K_S | 59 | 52 | 1/6 |
| H_8-15 from f16, Q4_K_M | 63 | | 0/6 |
| **H_8-15 from f16, Q4_K_M + imatrix** | **65** | **68** | **0/6** |

Thinking off, temperature 1.0, top_k 20, top_p 0.95, presence penalty 1.5, seed 0. The held-out set was never used to
pick a build. On it the final build gains 16 questions over the Q3 one and loses none.

On a 150-problem sample of MATH-500 (seed 0, thinking off, served by Ollama) the final build scores **131/150 (87.3%,
95% Wilson interval 81.1% to 91.7%)**. See [the MATH-500 notes](#math-500-sample) for what that number does and does
not show.

## Against other uncensored Qwen3.5-9B builds

The two Heretic builds on Hugging Face closest in size, run on the same PC with the same tests and settings (each
author's own Q4_K_M):
[llmfan46/Qwen3.5-9B-Ultra-Uncensored-Heretic-GGUF](https://huggingface.co/llmfan46/Qwen3.5-9B-Ultra-Uncensored-Heretic-GGUF)
and
[mradermacher/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-GGUF](https://huggingface.co/mradermacher/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-GGUF).

| Model | Size | Dev (74) | Held-out (74) | MATH-500 sample (150) | Refusals (6) | Heretic test: refusal phrases (100) | Heretic test: keyword hits (100) |
|---|---|---|---|---|---|---|---|
| Original Qwen3.5-9B, Q3_K_S | | 57 | | | 6/6 | 96 | 96 |
| **This repo, H_8-15 Q4_K_M + imatrix** | 5.6 GB | 65 | **68** | **131 (87.3%)** | 0/6 | 1 | 40 |
| llmfan46 Ultra-Uncensored-Heretic | 5.5 GB | **68** | 60 | **131 (87.3%)** | 0/6 | 0 | 11 |
| DeepSeek-V4-Pro-Qwen3.5-9B heretic | 5.8 GB | 31 | 26 | 120 (80.0%) | 0/6 | 0 | 11 |

- llmfan46 leads on the dev set by 3, this repo on the held-out set by 8. On MATH-500 each solves 6 problems the
  other misses.
- The DeepSeek-V4-Pro distill answers battery questions with the bare answer and no working (median 6.5 tokens,
  against 187 for this repo), which costs it most of the arithmetic and date items. On MATH-500, which asks for
  steps, it reaches 80.0% (95% interval 72.9% to 85.6%).
- Heretic's refusal test is the first 100 prompts of `mlabonne/harmful_behaviors` (test split), 100 new tokens,
  scored with Heretic's keyword list (`refuse100.py`). Its list also matches words like "illegal" or "harmful", so
  this repo's 40 keyword hits are answers that mention them; only 1 of the 100 contains a refusal phrase. The answers
  were not kept, so how many of the 40 still comply is not checked.
- The loop check failed to start on the PC (`WinError 267`), so the two rivals ran without it; this repo's run had it,
  and it ended 2 problems as wrong. The first 23 DeepSeek-V4-Pro MATH-500 problems ran on an M4 Mac (Ollama,
  Metal), the rest on the PC.
- Raw files: `results/bat_<model>_nt.jsonl`, `results/held_<model>_nt.jsonl`, `results/refuse100_*.jsonl`,
  `results/math500/results-think-off-<model>.jsonl`; the queue is `windows/bench.ps1`.

## What was tried (dev set, thinking off)

| Build | Score | Note |
|---|---|---|
| Original | 57 | |
| H_0-15 (layers 0-15 restored) | 57 | |
| H_12-15 | 58 | |
| M_8-15 (only `ffn_down` of 8-15) | 58 | |
| **H_8-15** | **59** | best layer range, refusals 1/6 |
| H_8-15 + `attn_output`/`ssm_out` of 16-19 | 56 | refusals back to 5/6 |
| H_8-15 rebuilt from f16, Q4_K_M | 63 | precision: +4 |
| same + imatrix | 65 | calibration: +2 |
| same + `ffn_down`/`ssm_out`/`attn_output` at Q6_K | 65 | gains 5, loses 5: no better |
| Q5_K_M, Q6_K | | do not fit in 8 GB RAM + 4.3 GB VRAM |

Restoring layers plateaued at 56-59, within noise (the same model scores 1 point apart across runs). The step change
came from precision: the first restorations were done on Q3_K_S files, and moving to f16 sources was worth more than
any choice of layers.

Earlier runs with thinking on and a 4096-token cap (`results/results.txt`): abliterated 19/74, original 33/74,
H_8-15 39/74. Most failures there were answers that never finished.

What the model still misses: reversing a word, the weekday of a date, adding days to a date, counting letters. The
first three fail in every build, original included, so they look like limits of a 9B model working on tokens rather
than damage from abliteration or quantization.

## MATH-500 sample

- 150 problems drawn with seed 0, the Qwen3.5 model-card sampling for thinking off, 7000-token cap
  (`results/math500/eval.py`). 9 answers hit the cap, 2 were stopped by the loop check below, 9 had no `\boxed{}`.
- A loop check: every 300 s of generation, Claude Haiku reads the partial work and answers STUCK only if the model is
  going in circles; a stuck problem counts as wrong. It never marks an answer right.
- Red Hat reports 85.0% for the original Qwen3.5-9B. I have not checked that figure's settings (thinking mode, full
  500 or not, precision), and the original was not run under this protocol, so the two are not a like-for-like
  comparison. The honest claim is narrower: the repaired 4-bit build is in the original's range on competition math.

## Limits

- The refusal check is 6 prompts (`refuse.py`) scored by refusal phrases in the first 400 characters. "0/6" means
  these 6 were answered, not that the model never refuses. Only verdicts were kept, never the answers.
- The abliterated model was not run with thinking off on the full battery, so the table has no "abliterated, thinking
  off" row; its comparison is the thinking-on run above.
- One seed, one machine; differences of 1 or 2 questions out of 74 are noise.

## How

- `differ.py`, `same_bytes.py`, `inspect_gguf.py`: abliteration only changed `ffn_down` in layers 1-31, `ssm_out` in
  23 of the 24 DeltaNet layers, and `attn_output` in the 8 attention layers. Those are the only candidates.
- `mix.py`: copies chosen tensors from the original into the abliterated GGUF (byte copy, or an alpha blend written as
  Q8_0 for requantization).
- `make_tests.py`: generates the battery (25 categories: GSM8K items, arithmetic, dates, character tasks, code tracing,
  logic, format and instruction following, French), expected answers computed, never typed. Seed 0 is the dev set
  (`tests.jsonl`), another seed the held-out set (`tests_held.jsonl`).
- `battery.py`: runs a set against llama-server and scores it; `report` and `rescore` compare runs. `refuse.py`: the
  refusal check. `calib.py`: imatrix calibration text, 1000 prompts from other seeds with every dev and held-out
  prompt left out.
- `windows/`: the PowerShell run queues on the PC (`nt*.ps1`, `practice*.ps1`), one job at a time. They ran from one
  flat folder (`D:\qwen-edit`) holding the Python tools, the GGUF files and a llama.cpp build in `llama\`.
- `results/`: raw answers of every run (`bat_*` dev, `held_*` held-out), `notes/`: failure diagnoses.

Models: the huihui-ai abliterated Qwen3.5-9B and the original Qwen3.5-9B as GGUF, f16 sources from mradermacher.
Qwen3.5-9B is a hybrid: 24 gated-DeltaNet layers and 8 full-attention layers (3, 7, ..., 31). Python needs `gguf`
(from llama.cpp) for the GGUF tools and `sympy` for MATH-500 grading. `gsm8k_test.jsonl` is the GSM8K test split
(MIT license).

## Lessons from the hardware

- llama-server keeps old prompts in RAM up to `--cache-ram` (default 8192 MiB). On an 8 GB machine a battery run
  swapped down to 0.07 tok/s; `--cache-ram 0` keeps it flat at 6.5 tok/s.
- `--fit` (default) splits a 5.6 GB Q4_K_M between VRAM and RAM. A 6.9 GB Q6_K does not fit.
- Two llama-servers can both listen on port 8080 on Windows, and their answers mix. Each run waits until no server is
  left.
- Installed in Ollama at 64k context, the final build loads at 8.1 GB (4 GB in VRAM) and generates about 5 tok/s.
