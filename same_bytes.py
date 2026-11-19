"""Which tensors differ between two GGUFs (type or bytes): python same_bytes.py a.gguf b.gguf"""
import sys
import numpy as np
import gguf

a, b = (gguf.GGUFReader(p) for p in sys.argv[1:3])
tb = {t.name: t for t in b.tensors}
same = 0
for t in a.tensors:
    u = tb[t.name]
    if t.tensor_type == u.tensor_type and np.array_equal(np.asarray(t.data), np.asarray(u.data)):
        same += 1
    else:
        print("differs:", t.name, t.tensor_type.name, "->", u.tensor_type.name)
print(f"{same}/{len(a.tensors)} tensors byte-identical")
