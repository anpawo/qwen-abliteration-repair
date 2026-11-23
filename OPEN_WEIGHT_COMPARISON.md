# Open-weight models for 32 to 40 GB of RAM

Research snapshot: 23 November 2026. This compares published benchmarks and downloadable weights from 10 labs, including community abliterated versions. These are not new benchmarks run on local hardware.

## Shortlist

Start by comparing stock Qwen3.8-27B and Gemma 4 31B. Consider Nemotron 3.5 Bolt with a 40 GB memory budget, and Ministral 3 14B Reasoning for a smaller model. This is a shortlist inferred from published evidence, not a measured ranking on the intended PC.

The table is sorted by the reported GPQA Diamond score. Different labs use different prompts, reasoning budgets and evaluation systems; GPQA is not an overall intelligence percentage. Most stock scores were not measured on the exact compressed files listed here. Abliterated models do not inherit their stock model's benchmark scores.

## Published scores and weight sizes

GB means decimal gigabytes. Sizes are selected main weight files from Hugging Face metadata checked during this research, excluding optional vision projectors and drafters. The RAM column is a rough total-system target for short-context inference with room for the OS, not a measured peak or a fit guarantee. Longer contexts, vision and particular runtimes can require more.

| Lab | Model | Published GPQA Diamond (%) | Stock file (GB) | Abliterated file (GB) | Estimated system RAM target (GB) |
|---|---|---:|---:|---:|---:|
| Alibaba | [Qwen3.8-27B][b1] | 89.2 | [ 16.564 ][s1] | [ 16.811 ][a1] | 32 |
| NVIDIA | [Nemotron 3.5 Bolt 74B-A9B][b2] | 86.43 | [ 22.018 ][s2] | [ 29.081 ][a2] | 40 |
| Google | [Gemma 4 31B IT][b3] | 84.3 | [ 18.324 ][s3] | [ 18.687 ][a3] | 32 |
| Meta | [Muse Glimmer 30B][b4] | 83.5 | [ 16.757 ][s4] | [ 16.935 ][a4] | 32 |
| Z.ai | [GLM-4.7-Flash][b5] | 75.2 | [ 18.312 ][s5] | [ 18.133 ][a5] | 32 |
| Moonshot | [Kimi Linear 48B-A3B Instruct][b6] | 71.7 | [ 29.703 ][s6] | [ 29.703 ][a6] | 40 |
| OpenAI | [gpt-oss-20b high reasoning][b7] | 71.5 | [ 11.625 ][s7] | [ 15.805 ][a7] | 32 |
| Mistral | [Ministral 3 14B Reasoning][b8] | 71.2 | [ 8.239 ][s8] | [ 8.239 ][a8] | 32 |
| DeepSeek | [R1 Distill Qwen 32B][b9] | 62.1 | [ 19.851 ][s9] | [ 19.851 ][a9] | 32 |
| Ai2 | [Olmo 3.1 32B Think][b10] | 57.5 | [ 19.482 ][s10] | [ 19.482 (Instruct variant, not Think) ][a10] | 32 |

### Quantization and architecture differences

- Qwen uses the stock UD-Q4_K_M file; most other entries use Q4_K_M. These formats are not identical compression settings.
- Bolt uses NVIDIA's trained approximately 2-bit stock format (22.018 GB) and AtomicChat AD-IQ2_XS for the abliterated option (29.081 GB). This is not a matched-quantization comparison. AtomicChat's AD-IQ1_M_S is 21.940 GB, with lower reported MMLU accuracy.
- GPT-OSS stock and abliterated GGUF layouts differ; their file-size difference does not establish that abliteration itself adds parameters or memory.
- Olmo's verified abliterated download is **Olmo 3.1 32B Instruct**, while the stock benchmark and stock download are **Think**. They are not a direct before/after pair.
- MoE active parameter counts describe computation, not total weight storage. Kimi Linear 48B-A3B is the smaller candidate here, not the full Kimi flagship; DeepSeek R1 Distill Qwen 32B is a distilled model, not the full DeepSeek flagship.

### Selected file identifiers

These names make it possible to recover the exact format rather than choosing another file from a repository with many quantizations.

| Model | Stock filename | Abliterated filename or format |
|---|---|---|
| Qwen | `Qwen3.8-27B-UD-Q4_K_M.gguf` | `Huihui-Qwen3.8-27B-abliterated.Q4_K_M.gguf` |
| Bolt | Main GGUF in NVIDIA's 24GB GGUF repository | AtomicChat `AD-IQ2_XS` |
| Gemma | `gemma-4-31B-it-Q4_K_M.gguf` | `Huihui-gemma-4-31B-it-abliterated.Q4_K_M.gguf` |
| Muse Glimmer | `Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf` | `Muse-Glimmer-30B-Abliterated-Q4_K_M.gguf` |
| GLM | `Q4_K_M` | `Huihui-GLM-4.7-Flash-abliterated.Q4_K_M.gguf` |
| Kimi Linear | `Q4_K_M` | `Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated.Q4_K_M.gguf` |
| GPT-OSS | `Q4_K_M` | `gpt-oss-20b-heretic.Q4_K_M.gguf` |
| Ministral | `Q4_K_M` | Author's `Q4_K_M` |
| DeepSeek | `Q4_K_M` | `DeepSeek-R1-Distill-Qwen-32B-abliterated-Q4_K_M.gguf` |
| Olmo | Think `Q4_K_M` | `Olmo-3.1-32B-Instruct-ARA-heretic.Q4_K_M.gguf` |

Muse Glimmer's optional drafter is about 1.631 GB and its vision projector about 1.400 GB. Bolt's stock vision projector is about 1.734 GB; these are additional files, not included in the main-weight sizes above. Runtime loading and caches add memory beyond file size.

## What was actually measured after abliteration

A refusal test measures whether an answer starts or behaves like a refusal. It does not establish reasoning quality. KL divergence measures a distribution change on the sampled data, not retained accuracy on unseen tasks.

| Release or comparison | Publisher's paired result | What it establishes |
|---|---|---|
| Qwen3.8-27B stock vs Huihui | GSM8K: 112/128 correct for both (87.5%); harmful-prompt refusals: 298/300 to 3/300 | Small paired test, not a full GPQA result or proof of identical general capability |
| Bolt stock 22.018 GB vs AtomicChat AD-IQ2_XS 29.081 GB | MMLU, 2,000 questions: 80.45% to 81.0% | Different compression and size; cannot attribute the difference to abliteration |
| Bolt BF16 before/after AtomicChat | MMLU, 2,000 questions: 81.35% to 81.75%, reported p = 0.29 | No demonstrated accuracy improvement in this test |
| Ministral coder3101 Heretic | Refusals: 97/100 to 7/100; KL 0.0172 | Refusal reduction; the copied stock benchmark table is not a new post-edit quality evaluation |
| GPT-OSS p-e-w Heretic | Refusals: 100/100 to 58/100; KL 0.96 | This particular edit still refused many prompts in its author's test |

Sources: [Qwen paired evaluation](https://huggingface.co/w3joe/Qwen3.8-27B-abliterated), [AtomicChat Bolt report][a2], [coder3101 Ministral report](https://huggingface.co/coder3101/Ministral-3-14B-Reasoning-2512-heretic), [p-e-w GPT-OSS report](https://huggingface.co/p-e-w/gpt-oss-20b-heretic).

AtomicChat also reports 79.0% MMLU for its 21.940 GB AD-IQ1_M_S file, against 80.45% for stock at a similar size. For the 29.081 GB file it reports 2/30 refusals with thinking enabled. Its refusal classification uses opening phrases and can miss other refusal forms. Its compressed vision path was not tested in that report.

For the exact Gemma, Muse Glimmer, GLM, Kimi and DeepSeek quantized downloads listed above, equivalent paired reasoning results were not verified. The Olmo download is a different variant. Their availability establishes neither preserved benchmark scores nor zero refusals.

### Related reports that must not be substituted for the selected files

- [dudeman2512 Muse Glimmer](https://huggingface.co/dudeman2512/Muse-Glimmer-30B-abliterated) reports 2,348/7,011 refusals before and 88/7,011 after, with KL 0.2241. This is not a reasoning benchmark and was not established as the source of the selected The-freezer quantization.
- [Torbeck GLM](https://huggingface.co/Torbeck/GLM-4.7-Flash-abliterated) reports refusals from 92/100 to 1/100 with KL 0.0133. It is a different edit from the Huihui file in the table.
- [Independent abliteration study](https://arxiv.org/html/2611.17846v1) evaluates multiple edits and models, including Qwen, Gemma, Olmo and Mistral. Its capability tests use fixed subsets and thinking disabled; they do not supply a matched reasoning-on benchmark for all 10 selected releases.

## Download and comparison caveats

The original Huihui Kimi abliterated repository returned HTTP 401 during research, while its GGUF mirror listed above was accessible. A search result or historical model card alone is not proof that weights remain downloadable.

Other options examined included NVIDIA Lightning 30B-A3B and Magistral Small 1.2 24B. The table selects Bolt and Ministral respectively; it does not claim these are each lab's best model on every task. Full-size flagships generally require much more storage and memory than their active-parameter count suggests. API-only releases and edits that also include fine-tuning must not be treated as equivalent downloadable, pure-abliteration comparisons.

## Hardware and training implications

More system RAM allows larger models to load and can avoid swapping. It does not increase a discrete GPU's VRAM or guarantee faster generation. A larger model mostly running on the CPU may generate more slowly than a smaller model that fits on the GPU. A Mac's unified-memory budget is shared with the OS and other apps. No local speed, peak RAM, backend compatibility or 32/40 GB fit was measured for these candidates.

The file sizes above concern inference, not training. LoRA learns smaller low-rank weight updates while keeping the base weights frozen; QLoRA also stores the base model in a quantized form. Training still needs memory for activations, gradients, optimizer state and the selected sequence length. An inference fit is not a training fit.

Individual weights can be changed, but reasoning errors are not normally stored in one identifiable set of wrong-answer cells. Comparing normal and abliterated weights identifies the editing operation, not the cause of every mistake. Better data, architecture, pretraining, post-training and inference-time reasoning all affect quality, so extra RAM alone cannot turn a smaller model into a frontier model.

## A controlled next benchmark

No new model evaluation, training run or model-weight download was started for this comparison.

For an actual local comparison, choose a stock model and its matching abliterated edit, use the same quantization, runtime, prompts, chat template, thinking budget, sampling, context and seeds, and record peak memory, tokens per second and answer quality. Preserve a fresh held-out set for the eventual training experiment. Keep refusal tests separate from capability tests, and count timed-out or capped answers consistently.

Begin with stock Qwen and Gemma, then the matched edit of whichever works better on the intended hardware and tasks. Only consider fine-tuning after this baseline identifies repeatable failure categories; do not train on the same held-out questions used to claim improvement.

## Sources and downloadable weights

Benchmark links below identify the lab's model card or original report; stock and abliterated links identify the exact repository inspected. Model availability and scores are a dated snapshot, not live guarantees.

### Alibaba: Qwen3.8-27B

- [Published benchmark][b1]
- [Stock GGUF: unsloth/Qwen3.8-27B-GGUF][s1]
- [Community GGUF: mradermacher/Huihui-Qwen3.8-27B-abliterated-GGUF][a1]

### NVIDIA: Nemotron 3.5 Bolt 74B-A9B

- [Published benchmark][b2]
- [Stock GGUF: nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF][s2]
- [Community GGUF: AtomicChat/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Uncensored-GGUF][a2]

### Google: Gemma 4 31B IT

- [Published benchmark][b3]
- [Stock GGUF: unsloth/gemma-4-31B-it-GGUF][s3]
- [Community GGUF: mradermacher/Huihui-gemma-4-31B-it-abliterated-GGUF][a3]

### Meta: Muse Glimmer 30B

- [Published benchmark][b4]
- [Stock GGUF: meta-models/Muse-Glimmer-30B-GGUF][s4]
- [Community GGUF: The-freezer/Muse-Glimmer-30B-Abliterated-GGUF][a4]

### Z.ai: GLM-4.7-Flash

- [Published benchmark][b5]
- [Stock GGUF: unsloth/GLM-4.7-Flash-GGUF][s5]
- [Community GGUF: mradermacher/Huihui-GLM-4.7-Flash-abliterated-GGUF][a5]

### Moonshot: Kimi Linear 48B-A3B Instruct

- [Published benchmark][b6]
- [Stock GGUF: mradermacher/Kimi-Linear-48B-A3B-Instruct-GGUF][s6]
- [Community GGUF: mradermacher/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated-GGUF][a6]

### OpenAI: gpt-oss-20b high reasoning

- [Published benchmark][b7]
- [Stock GGUF: unsloth/gpt-oss-20b-GGUF][s7]
- [Community GGUF: mradermacher/gpt-oss-20b-heretic-GGUF][a7]

### Mistral: Ministral 3 14B Reasoning

- [Published benchmark][b8]
- [Stock GGUF: unsloth/Ministral-3-14B-Reasoning-2512-GGUF][s8]
- [Community GGUF: coder3101/Ministral-3-14B-Reasoning-2512-heretic-GGUF][a8]

### DeepSeek: R1 Distill Qwen 32B

- [Published benchmark][b9]
- [Stock GGUF: unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF][s9]
- [Community GGUF: bartowski/DeepSeek-R1-Distill-Qwen-32B-abliterated-GGUF][a9]

### Ai2: Olmo 3.1 32B Think

- [Published benchmark][b10]
- [Stock GGUF: unsloth/Olmo-3.1-32B-Think-GGUF][s10]
- [Community GGUF: mradermacher/Olmo-3.1-32B-Instruct-ARA-heretic-GGUF][a10]

[b1]: https://huggingface.co/Qwen/Qwen3.8-27B
[s1]: https://huggingface.co/unsloth/Qwen3.8-27B-GGUF
[a1]: https://huggingface.co/mradermacher/Huihui-Qwen3.8-27B-abliterated-GGUF
[b2]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB
[s2]: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF
[a2]: https://huggingface.co/AtomicChat/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Uncensored-GGUF
[b3]: https://huggingface.co/google/gemma-4-31B-it
[s3]: https://huggingface.co/unsloth/gemma-4-31B-it-GGUF
[a3]: https://huggingface.co/mradermacher/Huihui-gemma-4-31B-it-abliterated-GGUF
[b4]: https://huggingface.co/meta-models/Muse-Glimmer-30B
[s4]: https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF
[a4]: https://huggingface.co/The-freezer/Muse-Glimmer-30B-Abliterated-GGUF
[b5]: https://huggingface.co/zai-org/GLM-4.7-Flash
[s5]: https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF
[a5]: https://huggingface.co/mradermacher/Huihui-GLM-4.7-Flash-abliterated-GGUF
[b6]: https://arxiv.org/html/2510.26692v1
[s6]: https://huggingface.co/mradermacher/Kimi-Linear-48B-A3B-Instruct-GGUF
[a6]: https://huggingface.co/mradermacher/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated-GGUF
[b7]: https://arxiv.org/html/2508.10925v1
[s7]: https://huggingface.co/unsloth/gpt-oss-20b-GGUF
[a7]: https://huggingface.co/mradermacher/gpt-oss-20b-heretic-GGUF
[b8]: https://arxiv.org/html/2601.08584v1
[s8]: https://huggingface.co/unsloth/Ministral-3-14B-Reasoning-2512-GGUF
[a8]: https://huggingface.co/coder3101/Ministral-3-14B-Reasoning-2512-heretic-GGUF
[b9]: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
[s9]: https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF
[a9]: https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-abliterated-GGUF
[b10]: https://huggingface.co/allenai/Olmo-3.1-32B-Think
[s10]: https://huggingface.co/unsloth/Olmo-3.1-32B-Think-GGUF
[a10]: https://huggingface.co/mradermacher/Olmo-3.1-32B-Instruct-ARA-heretic-GGUF
