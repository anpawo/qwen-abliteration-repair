"""Weight-space edit after MIT's "Sparks of Weight-Space Programming": find the MLP neurons that
fire when the model re-checks an answer it already has, take the one direction they write
together, and remove it from those neurons' output columns of ffn_down.

usage: python edit.py <model.gguf> <recheck.imatrix.gguf> <solve.imatrix.gguf> scan
       python edit.py <model.gguf> <recheck.imatrix.gguf> <solve.imatrix.gguf> <out.gguf> <L1,L2> [k] [--null]
--null rewrites the same tensors as Q8_0 without the edit (control for the format change).
"""
import sys
import numpy as np
import gguf
from gguf.scripts.gguf_new_metadata import copy_with_new_metadata

SRC, POS, NEG = sys.argv[1:4]
Q8 = gguf.GGMLQuantizationType.Q8_0


def act(path):
    """mean input of ffn_down per neuron (kind=in_sum) or its mean square (kind=in_sum2)"""
    t = {x.name: np.asarray(x.data, np.float64).ravel() for x in gguf.GGUFReader(path).tensors}
    return lambda L, kind: t[f"blk.{L}.ffn_down.weight.{kind}"] / t[f"blk.{L}.ffn_down.weight.counts"][0]


pos, neg = act(POS), act(NEG)
model = gguf.GGUFReader(SRC)
idx = {t.name: i for i, t in enumerate(model.tensors)}
n_layer = int(model.fields["qwen35.block_count"].contents())


def down(L):
    t = model.tensors[idx[f"blk.{L}.ffn_down.weight"]]
    W = gguf.quants.dequantize(t.data, t.tensor_type)
    assert W.shape == (4096, 12288), W.shape
    return W


def pick(L, W, k):
    """d: unit direction the MLP writes more of while re-checking; top: the k neurons carrying most of it;
    rel: size of that extra write next to the MLP's usual output; carried: share of it the k neurons carry"""
    W = W.astype(np.float64)
    dm = pos(L, "in_sum") - neg(L, "in_sum")
    delta = W @ dm
    d = delta / np.linalg.norm(delta)
    contrib = dm * (d @ W)  # sums to |delta|
    top = np.argsort(contrib)[-k:]
    typical = np.sqrt(((pos(L, "in_sum2") + neg(L, "in_sum2")) / 2) @ (W ** 2).sum(0))
    return d, top, np.linalg.norm(delta) / typical, contrib[top].sum() / contrib.sum()


if sys.argv[4] == "scan":
    print("layer  rel_size  carried_by_64  carried_by_256")
    for L in range(n_layer):
        W = down(L)
        _, _, rel, c64 = pick(L, W, 64)
        c256 = pick(L, W, 256)[3]
        print(f"{L:5d}  {rel:8.3f}  {c64:13.3f}  {c256:14.3f}", flush=True)
    sys.exit()

OUT, layers = sys.argv[4], [int(x) for x in sys.argv[5].split(",")]
k = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6].isdigit() else 64
for L in layers:
    W = down(L)
    d, top, rel, carried = pick(L, W, k)
    if "--null" not in sys.argv:
        S = W[:, top].astype(np.float64)
        W[:, top] = (S - np.outer(d, d @ S)).astype(np.float32)
        assert np.abs(d @ W[:, top].astype(np.float64)).max() < 1e-3
    q = gguf.quants.quantize(W, Q8)
    i = idx[f"blk.{L}.ffn_down.weight"]
    model.tensors[i] = model.tensors[i]._replace(data=q, tensor_type=Q8, n_bytes=q.nbytes)
    print(f"layer {L}: {k} columns, rel_size={rel:.3f} carried={carried:.3f}", flush=True)

w = gguf.GGUFWriter(OUT, arch=model.fields["general.architecture"].contents(), endianess=model.endianess)
if "general.alignment" in model.fields:
    w.data_alignment = int(model.fields["general.alignment"].contents())
copy_with_new_metadata(model, w, {}, [])
print("wrote", OUT, f"({len(layers) * k * 4096} weights edited)")
