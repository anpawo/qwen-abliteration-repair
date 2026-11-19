"""python differ.py <a.gguf> <b.gguf>: which tensors differ, grouped by kind, with their layers."""
import sys
from collections import defaultdict
import gguf
a, b = gguf.GGUFReader(sys.argv[1]), gguf.GGUFReader(sys.argv[2])
src = {t.name: t for t in b.tensors}
kinds = defaultdict(list)
for t in a.tensors:
    if not (t.data == src[t.name].data).all():
        parts = t.name.split(".")
        kinds[parts[2] if parts[0] == "blk" else parts[0]].append(parts[1] if parts[0] == "blk" else "-")
for k, layers in sorted(kinds.items()):
    print(f"{k:16s} {len(layers):2d}  {','.join(layers)}")
