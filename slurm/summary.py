"""One line per model from a results folder of the A100 runs: battery score per seed, refusal counts, MATH-500.
usage: python slurm/summary.py results/a100 [results/a100/search]"""
import glob, json, math, os, re, sys


def rows(f):
    return [json.loads(l) for l in open(f, encoding="utf-8")]


def wilson(k, n, z=1.96):
    p = k / n
    c, h = (p + z * z / (2 * n)) / (1 + z * z / n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return f"{p:.1%} [{c - h:.1%}, {c + h:.1%}]"


for d in sys.argv[1:]:
    names = sorted({re.sub(r"^bat_(.+)_nt_s\d+\.jsonl$", r"\1", os.path.basename(f)) for f in glob.glob(f"{d}/bat_*_nt_s*.jsonl")})
    print(f"{d}\nmodel | dev per seed (mean) | held per seed (mean) | refuse6 | refuse100 heretic/strict | MATH-500 off")
    for m in names:
        cells = []
        for kind in ("bat", "held"):
            fs = sorted(glob.glob(f"{d}/{kind}_{m}_nt_s*.jsonl"))
            s = [sum(r["ok"] for r in rows(f)) for f in fs if len(rows(f)) == 74]
            cells.append(f"{' '.join(map(str, s))} ({sum(s) / len(s):.1f})" if s else "")
        r6 = open(f"{d}/refuse6_{m}.txt").read().strip().splitlines()[-1].split("refused ")[-1] if os.path.exists(f"{d}/refuse6_{m}.txt") else ""
        f100 = f"{d}/refuse100_{m}.jsonl"
        r100 = f"{sum(r['heretic_match'] for r in rows(f100))}/{sum(r['strict_refusal'] for r in rows(f100))}" if os.path.exists(f100) else ""
        fm = f"{d}/math500_{m}_off.jsonl"
        mr = rows(fm) if os.path.exists(fm) else []
        math500 = f"{sum(r['correct'] for r in mr)}/{len(mr)} {wilson(sum(r['correct'] for r in mr), len(mr))}, capped {sum(r['done_reason'] == 'length' for r in mr)}" if mr else ""
        print(" | ".join([m, *cells, r6, r100, math500]))
