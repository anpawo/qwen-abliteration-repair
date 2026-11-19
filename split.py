"""Two corpora from the base answers: the reasoning just before the right answer first appears
(solving) and just after it (re-checking an answer it already has).
usage: python split.py base_train.jsonl solve.txt recheck.txt"""
import json, re, sys

MAXC = 6000
solve, recheck = [], []
for l in open(sys.argv[1], encoding="utf-8"):
    r = json.loads(l)
    t, g = r["thinking"], r["gold"]
    ans = str(int(g)) if g == int(g) else str(g)
    m = re.search(r"(=|is|:|equals|\*\*)\s*\$?\s*" + re.escape(ans) + r"(?![\d.])", t)
    if not m:
        continue
    n = min(m.end(), len(t) - m.end(), MAXC)
    if n < 300:
        continue
    solve.append(t[m.end() - n:m.end()])
    recheck.append(t[m.end():m.end() + n])
for path, parts in ((sys.argv[2], solve), (sys.argv[3], recheck)):
    open(path, "w", encoding="utf-8").write("\n\n".join(parts))
print(f"{len(solve)} answers used, {sum(map(len, solve))} chars per corpus")
