"""Abliterated model with a range of layers taken back, byte for byte, from the non-abliterated one.
usage: python mix.py <abliterated.gguf> <non-abliterated.gguf> <out.gguf> <first>-<last> [alpha] [kind,kind]
alpha > 0 keeps that share of the abliteration delta (stock + alpha * (abl - stock)), written as Q8_0 for llama-quantize;
kinds (ffn_down, ssm_out, attn_output) restrict which tensors change."""
import sys
import gguf
from gguf.scripts.gguf_new_metadata import copy_with_new_metadata

abl, orig = gguf.GGUFReader(sys.argv[1]), gguf.GGUFReader(sys.argv[2])
lo, hi = map(int, sys.argv[4].split("-"))
alpha = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
kinds = sys.argv[6].split(",") if len(sys.argv) > 6 else None
Q8 = gguf.GGMLQuantizationType.Q8_0
src = {t.name: t for t in orig.tensors}
n = 0
for i, t in enumerate(abl.tensors):
    if t.name.startswith("blk.") and lo <= int(t.name.split(".")[1]) <= hi and (not kinds or any(k in t.name for k in kinds)):
        u = src[t.name]
        assert u.tensor_type == t.tensor_type and u.data.shape == t.data.shape, t.name
        if (u.data == t.data).all():
            continue
        if alpha:
            S = gguf.quants.dequantize(u.data, u.tensor_type)
            q = gguf.quants.quantize(S + alpha * (gguf.quants.dequantize(t.data, t.tensor_type) - S), Q8)
            abl.tensors[i] = t._replace(data=q, tensor_type=Q8, n_bytes=q.nbytes)
        else:
            abl.tensors[i] = t._replace(data=u.data)
        n += 1
w = gguf.GGUFWriter(sys.argv[3], arch=abl.fields["general.architecture"].contents(), endianess=abl.endianess)
if "general.alignment" in abl.fields:
    w.data_alignment = int(abl.fields["general.alignment"].contents())
copy_with_new_metadata(abl, w, {}, [])
print(f"{n} tensors of layers {lo}-{hi} restored, alpha {alpha}, kinds {kinds or 'all'}")
