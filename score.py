import json, sys

tag, files = sys.argv[1], sys.argv[2:]
rows = [json.loads(l) for f in files for l in open(f, encoding="utf-8")]
n = len(rows)
ok = sum(r["correct"] for r in rows)
cap = sum(r["done_reason"] == "length" for r in rows)
print(f"{tag}: n={n} correct={ok} ({100 * ok / n:.0f}%) hit_cap={cap} ({100 * cap / n:.0f}%) "
      f"mean_tokens={sum(r['tokens'] for r in rows) / n:.0f} mean_secs={sum(r['secs'] for r in rows) / n:.0f}")
