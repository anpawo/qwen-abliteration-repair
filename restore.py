"""mix.py for safetensors at full precision: the abliterated model with every tensor that abliteration changed in layers
<first>-<last> copied back from the original. Shards with nothing restored are hard-linked, not copied.
usage: python restore.py <abliterated dir> <original dir> <out dir> <first>-<last> [name part,name part]
name parts (mlp.down_proj, linear_attn.out_proj, self_attn.o_proj) restrict which tensors change."""
import json, os, re, shutil, sys
import torch
from safetensors import safe_open
from safetensors.torch import save_file

abl, orig, out = sys.argv[1:4]
lo, hi = map(int, sys.argv[4].split("-"))
kinds = sys.argv[5].split(",") if len(sys.argv) > 5 else None
os.makedirs(out, exist_ok=True)
where = json.load(open(f"{orig}/model.safetensors.index.json"))["weight_map"]
n = 0
for f in sorted(os.listdir(abl)):
    src, dst = f"{abl}/{f}", f"{out}/{f}"
    if os.path.exists(dst):
        os.remove(dst)
    if not f.endswith(".safetensors"):
        if os.path.isfile(src):
            shutil.copy(src, dst)
        continue
    tensors, changed = {}, 0
    with safe_open(src, "pt") as a:
        meta = a.metadata()
        for k in a.keys():
            t = a.get_tensor(k)
            m = re.search(r"language_model\.layers\.(\d+)\.", k)
            if m and lo <= int(m[1]) <= hi and (not kinds or any(x in k for x in kinds)):
                with safe_open(f"{orig}/{where[k]}", "pt") as o:
                    u = o.get_tensor(k)
                assert u.shape == t.shape and u.dtype == t.dtype, k
                if not torch.equal(u, t):
                    t, changed = u, changed + 1
            tensors[k] = t
    if changed:
        save_file(tensors, dst, meta)
    else:
        os.link(src, dst)
    n += changed
print(f"{n} tensors of layers {lo}-{hi} restored, kinds {kinds or 'all'}")
