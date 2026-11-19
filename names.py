"""python names.py <model.gguf> <layer>...: tensor names and types of those layers, plus the non-block tensors."""
import sys
import gguf
r = gguf.GGUFReader(sys.argv[1])
for t in r.tensors:
    parts = t.name.split(".")
    if not t.name.startswith("blk.") or parts[1] in sys.argv[2:]:
        print(t.name, t.tensor_type.name)
