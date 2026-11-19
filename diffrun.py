"""Per-question diff of two battery runs: python diffrun.py <before.jsonl> <after.jsonl>"""
import json, sys
a, b = ({r["id"]: r["ok"] for r in map(json.loads, open(f, encoding="utf-8"))} for f in sys.argv[1:3])
print("gained:", [k for k in b if b[k] and not a.get(k)])
print("lost:", [k for k in b if a.get(k) and not b[k]])
print("still failing:", [k for k in b if not b[k]])
