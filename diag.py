"""Per failing test of a scored battery file: cap hit, whether the expected answer shows up in the thinking, re-check markers, thinking tail.
python diag.py <tests.jsonl> <tag>.scored.jsonl"""
import json, re, sys

tests = {t["id"]: t for t in map(json.loads, open(sys.argv[1], encoding="utf-8"))}
for r in map(json.loads, open(sys.argv[2], encoding="utf-8")):
    if r["ok"]:
        continue
    v = tests[r["id"]]["value"]
    vs = [str(int(v)) if isinstance(v, float) and v == int(v) else str(v)] if not isinstance(v, (list, dict)) or v is None else [str(x) for x in v][:1]
    th = r["thinking"]
    seen = any(s and s.lower() in th.lower() for s in vs)
    waits = len(re.findall(r"\b(wait|let me (?:re-?check|verify|double-check)|double-check)\b", th, re.I))
    tail = re.sub(r"\s+", " ", th[-160:])
    print(f"{r['id']:<18} {r['done_reason']:<6} {r['tokens']:>5} gold_seen={'Y' if seen else 'n'} rechecks={waits:>3} | {tail}")
