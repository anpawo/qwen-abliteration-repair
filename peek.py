"""Show the start and end of one saved answer: python peek.py <file.jsonl> <row> [head] [tail]"""
import json, sys

rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
r = rows[int(sys.argv[2])]
head, tail = int(sys.argv[3]) if len(sys.argv) > 3 else 1500, int(sys.argv[4]) if len(sys.argv) > 4 else 2500
t = r["thinking"]
print({k: r[k] for k in ("i", "gold", "pred", "correct", "done_reason", "tokens")}, "thinking chars:", len(t))
print(t[:head], "\n=====\n", t[-tail:], "\n=====\n", r["content"][-400:])
