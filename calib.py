"""Calibration text for an imatrix: prompts of the battery's categories drawn with seeds 100-139 (ChatGPT's mix,
07/11), with every prompt that is also in the dev or held-out set left out.
python calib.py <out.txt>"""
import json, subprocess, sys

taken = {json.loads(l)["prompt"] for f in ("tests.jsonl", "tests_held.jsonl") for l in open(f, encoding="utf-8")}
seen, out, dropped = set(), [], 0
for seed in range(100, 140):
    subprocess.run([sys.executable, "make_tests.py", str(seed), "calib_tmp.jsonl"], check=True, capture_output=True)
    for line in open("calib_tmp.jsonl", encoding="utf-8"):
        p = json.loads(line)["prompt"]
        if p in taken:
            dropped += 1
        elif p not in seen:
            seen.add(p)
            out.append(p)
open(sys.argv[1], "w", encoding="utf-8", newline="\n").write("\n\n".join(out) + "\n")
print(f"{len(out)} prompts kept, {dropped} dropped as dev or held-out")
