import collections, sys
import gguf

r = gguf.GGUFReader(sys.argv[1])
for k in r.fields:
    if k.startswith(("general.architecture", "general.name", "qwen35", "general.file_type")):
        f = r.fields[k]
        v = f.contents() if hasattr(f, "contents") else f.parts[-1]
        print(k, "=", v if not isinstance(v, list) or len(v) < 50 else f"list[{len(v)}]")
types = collections.Counter()
for t in r.tensors:
    types[(t.name.split(".", 2)[-1] if t.name.startswith("blk.") else t.name, t.tensor_type.name)] += 1
for (name, ty), n in sorted(types.items()):
    print(f"{n:3d} x {name} {ty}")
t = next(t for t in r.tensors if t.name == "blk.16.ffn_down.weight")
print("ffn_down shape", t.shape.tolist(), t.tensor_type.name)
import numpy as np
for q in ("Q8_0", "Q3_K", "Q4_K", "Q5_K", "Q6_K"):
    try:
        gguf.quants.quantize(np.ones((2, 256), np.float32), gguf.GGMLQuantizationType[q]); print(q, "quantize ok")
    except Exception as e:
        print(q, "quantize:", type(e).__name__)
