---
license: apache-2.0
base_model:
- huihui-ai/Huihui-Qwen3.5-9B-abliterated
- Qwen/Qwen3.5-9B
tags:
- gguf
- abliterated
- qwen3.5
- llama.cpp
- ollama
---

# Qwen3.5-9B abliterated, repaired (GGUF, Q4_K_M + imatrix)

[huihui-ai/Huihui-Qwen3.5-9B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.5-9B-abliterated) with every
tensor that abliteration changed in layers 8-15 copied back from the original
[Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B), then rebuilt from f16 at Q4_K_M with an importance matrix.
The aim: get back the reasoning abliteration costs while keeping its answers. It fits a 4 GB GPU with RAM offload.

Code, test sets, every run's raw answers and what did not work: https://github.com/anpawo/qwen-abliteration-repair

## Results

| Model | Dev set (74) | Held-out set (74) | Refusals (6 prompts) |
|---|---|---|---|
| Original Qwen3.5-9B, Q3_K_S | 57 | | 6/6 |
| **This model** | **65** | **68** | **0/6** |

Thinking off, temperature 1.0, top_k 20, top_p 0.95, presence penalty 1.5. The held-out set was never used to pick a
build. On a 150-problem sample of MATH-500 (thinking off) it scores 131/150 (87.3%, 95% interval 81.1% to 91.7%).

Limits: the refusal check is 6 prompts, not a safety evaluation; one seed; differences of 1-2 questions are noise.
The model still fails at reversing words, weekday and date arithmetic, and counting letters.

## Files

- `H_8-15.Q4_K_M.im.gguf` (5.6 GB): the model.
- `H_8-15.calib.imatrix.gguf`: the importance matrix used to quantize it.
- `Modelfile`: Ollama import with the sampling above.

## Use

```
ollama create qwen3.5-9b-abl-repaired -f Modelfile
```

or `llama-server -m H_8-15.Q4_K_M.im.gguf --cache-ram 0` (the default prompt cache swaps on 8 GB machines).

## Responsibility

Abliteration removes the refusal behaviour. This model will answer requests the original declines; you are
responsible for how you use it and for adding your own safeguards where needed.
