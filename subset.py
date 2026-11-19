"""python subset.py <tests.jsonl> <out.jsonl> <id>...: the named tests only (for a single-item rerun)."""
import json, sys
ids = set(sys.argv[3:])
rows = [l for l in open(sys.argv[1], encoding="utf-8") if json.loads(l)["id"] in ids]
assert len(rows) == len(ids), "unknown id"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").writelines(rows)
