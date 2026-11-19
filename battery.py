"""Test battery on llama-server (LLAMA_PORT), two requests at a time, resumable.

python battery.py <tests.jsonl> <out.jsonl>     run (thinking on, the Ollama Modelfile sampling, cap NUM_PREDICT)
python battery.py report <out.jsonl>...         pass count per category, one column per run
python battery.py rescore <tests.jsonl> <out.jsonl>...   regrade into <out>.scored.jsonl, raw file untouched, no GPU
python battery.py selftest
"""
import concurrent.futures as cf, json, os, re, sys, threading, time, urllib.request

MAX = int(os.environ.get("NUM_PREDICT", 4096))
FR = set("le la les est des du de et en une un que parce car il qui sont dans par plus lumière ciel bleu".split())
EN = set("the is are because of and light sky blue which".split())


def boxed(s):
    i = s.rfind("\\boxed{")
    if i < 0:
        return None
    depth = 1
    for k in range(i + 7, len(s)):
        depth += {"{": 1, "}": -1}.get(s[k], 0)
        if depth == 0:
            return s[i + 7:k]
    return None


def plain(s, lower=True):
    for _ in range(3):
        s = re.sub(r"\\(?:text|texttt|mathrm|textbf|mathbf|operatorname)\{([^{}]*)\}", r"\1", s)
    s = s.replace("$", "").replace("\\", "").strip().strip(".").strip("'\"`*").strip()
    return s.lower() if lower else s


NEG = {"not", "no", "is", "isnt", "wrong", "incorrect", "false", "never", "approximately", "about"}
MODS = {"light", "dark", "bright", "pale", "deep", "sky", "royal", "forest", "hot", "baby", "navy"}


def number(s, vocab=frozenset()):
    """A boxed answer that is one number or fraction, followed by at most two unit words taken from the question; else None."""
    s = plain(re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", s))
    m = re.fullmatch(r"(-?\d*\.?\d+)(?:\s*/\s*(-?\d*\.?\d+))?((?:\s*[a-z]+){0,2})", re.sub(r"(?<=\d),(?=\d{3})", "", s))
    if not m or (m[2] and float(m[2]) == 0) or any(w in NEG or w not in vocab for w in m[3].split()):
        return None
    return float(m[1]) / float(m[2]) if m[2] else float(m[1])


def canon(s):
    s = re.sub(r"^[-*•]\s*", "", s.strip().lower().replace("’", "'")).strip(" .*")
    return re.sub(r"(?<!s)s$", "", re.sub(r"ies$", "y", s))


def norm_text(s):
    return re.sub(r"\s+", " ", re.sub(r"[\"'«»*“”.!]", "", s.lower())).strip()


def ok(t, c):
    k, v, b, text = t["check"], t["value"], boxed(c), c.strip()
    a = plain(b if b is not None else text)
    words = re.findall(r"[A-Za-zÀ-ÿ'-]+", text)
    if k in ("number", "exact", "exact_case", "exact_any", "letters") and b is None:
        return False
    if k == "number":
        x = number(b, frozenset(re.findall(r"[a-z]+", t.get("prompt", "").lower())))
        return x is not None and abs(x - v) <= t.get("tol", 1e-6)
    if k == "exact":
        return a == str(v).lower()
    if k == "exact_case":
        return plain(b, lower=False) == v
    if k == "exact_any":
        return a in v
    if k == "letters":
        return re.sub(r"[^a-z]", "", a) == v
    if k == "sequence":
        return [float(x) for x in re.findall(r"-?\d*\.?\d+", text)] == [float(x) for x in v]
    if k == "text_any":
        return norm_text(text) in v
    if k == "word_count":
        return len(words) == v
    if k == "csv_count":
        parts = [canon(p) for p in text.rstrip(".").split(",")]
        return len(parts) == v and len(set(parts)) == v and all(
            p.split() and p.split()[-1] in t["pool"] and all(w in MODS for w in p.split()[:-1]) for p in parts)
    if k == "lowercase":
        return any(ch.isalpha() for ch in text) and text == text.lower()
    if k == "uppercase":
        return any(ch.isalpha() for ch in text) and text == text.upper()
    if k == "no_letter":
        return t["letter"] not in text.lower() and len(words) >= v
    if k in ("json_keys", "json_equal"):
        try:
            j = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", text))
        except ValueError:
            return False
        if k == "json_equal":
            return j == v
        types = {"str": str, "num": (int, float)}
        return isinstance(j, dict) and all(isinstance(j.get(key), types[ty]) and not isinstance(j.get(key), bool) for key, ty in v.items())
    if k == "distinct_lines":
        lines = [canon(l) for l in text.splitlines() if l.strip()]
        pool = {canon(p) for p in t["pool"]}
        return len(lines) == v and len(set(lines)) == v and all(l in pool for l in lines)
    if k == "french":
        w = [x.lower() for x in words]
        return sum(x in FR for x in w) >= 3 and sum(x in EN for x in w) <= 1
    raise ValueError(k)


def run(t):
    t0 = time.time()
    req = urllib.request.Request(f"http://127.0.0.1:{os.environ['LLAMA_PORT']}/v1/chat/completions", json.dumps({
        "messages": [{"role": "user", "content": t["prompt"]}], "max_tokens": MAX, "seed": 0, "top_k": 20, "top_p": 0.95,
        "temperature": float(os.environ.get("SAMPLE_TEMP", 1.0)),
        "presence_penalty": float(os.environ.get("SAMPLE_PRESENCE", 1.5)),
        "chat_template_kwargs": {"enable_thinking": os.environ.get("THINK", "1") == "1"}}).encode(),
        {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=7200))
    ch = r["choices"][0]
    c = ch["message"].get("content") or ""
    return {"id": t["id"], "cat": t["cat"], "kind": t.get("kind", "fact"), "ok": ok(t, c), "done_reason": ch["finish_reason"],
            "tokens": r["usage"]["completion_tokens"], "secs": round(time.time() - t0),
            "content": c, "thinking": ch["message"].get("reasoning_content") or ""}


def report(files):
    runs = [[json.loads(l) for l in open(f, encoding="utf-8")] for f in files]
    cats = list(dict.fromkeys(r["cat"] for rows in runs for r in rows))
    print("category".ljust(16) + "".join(os.path.basename(f).replace(".jsonl", "")[:14].rjust(15) for f in files))
    for c in cats + ["FACT", "FORMAT", "TOTAL", "capped"]:
        cells = []
        for rows in runs:
            sel = [r for r in rows if c in ("TOTAL", "capped") or r["cat"] == c or r.get("kind", "fact") == c.lower()]
            n = sum(r["done_reason"] == "length" for r in sel) if c == "capped" else sum(r["ok"] for r in sel)
            cells.append(f"{n}/{len(sel)}".rjust(15))
        print(c.ljust(16) + "".join(cells))


if sys.argv[1] == "selftest":
    T = lambda check, value, **kw: {"check": check, "value": value, **kw}
    assert ok(T("number", 1 / 6, tol=0.001), "so \\boxed{\\frac{1}{6}}") and ok(T("number", 12600, prompt="How many seconds"), "\\boxed{12,600 seconds}")
    assert not ok(T("number", 9.9), "\\boxed{9.11}") and ok(T("exact", "Sunday"), "\\boxed{\\text{Sunday}}")
    assert ok(T("letters", "mhtirogla"), "\\boxed{m-h-t-i-r-o-g-l-a}") and ok(T("sequence", [-4, 0, 7]), "-4, 0, 7")
    assert ok(T("json_keys", {"name": "str", "age": "num"}), '```json\n{"name": "Ann", "age": 31}\n```')
    assert not ok(T("no_letter", 3, letter="e"), "The cat sat") and ok(T("no_letter", 3, letter="e"), "A cat sat down")
    assert ok(T("distinct_lines", 2, pool=["kenya", "egypt"]), "Kenya\nEgypt") and not ok(T("distinct_lines", 2, pool=["a"]), "a\na")
    assert not ok(T("exact_case", "ECRUOS"), "\\boxed{ecruos}") and ok(T("exact_case", "ECRUOS"), "\\boxed{\\text{ECRUOS}}")
    assert not ok(T("number", 4, prompt="How many times is 4"), "\\boxed{4 is wrong}") and not ok(T("number", 0.25, tol=0.001), "\\boxed{0.25\\%}")
    assert not ok(T("csv_count", 3, pool=["red", "blue", "green"]), "not red, not blue, not green")
    assert ok(T("number", 8.05, tol=0.006, prompt="Convert 5 miles to km"), "\\boxed{8.05 \\text{ km}}")
    assert ok(T("french", None), "Le ciel est bleu parce que la lumière bleue est diffusée.")
    assert not ok(T("number", 379757670), "\\boxed{379757770}") and not ok(T("number", 4), "\\boxed{4/0}")
    assert not ok(T("number", 4), "The answer is not 4.") and not ok(T("number", 4), "\\boxed{not 4}")
    assert not ok(T("json_keys", {"name": "str", "age": "num"}), '{"name":"Ann","age":true}')
    assert not ok(T("csv_count", 3, pool=["red", "blue", "green"]), "cat, dog, table") and ok(T("csv_count", 3, pool=["red", "blue", "green"]), "Red, light blue, green.")
    assert not ok(T("distinct_lines", 12, pool=["chad"]), "\n".join("Chad " + chr(97 + i) for i in range(12)))
    assert not ok(T("distinct_lines", 2, pool=["apple", "pear"]), "a\nb") and ok(T("distinct_lines", 2, pool=["apple", "cherry"]), "Apples\n- Cherries")
    assert not ok(T("exact_any", ["victor hugo", "hugo"]), "Not Hugo.") and ok(T("exact_any", ["victor hugo", "hugo"]), "\\boxed{Victor Hugo}")
    assert not ok(T("text_any", ["the cat sleeps on the couch"]), "The cat is not on the couch.") and ok(T("text_any", ["the cat sleeps on the couch"]), "« The cat sleeps on the couch. »")
    print("selftest ok")
elif sys.argv[1] == "report":
    report(sys.argv[2:])
elif sys.argv[1] == "rescore":
    tests = {t["id"]: t for t in map(json.loads, open(sys.argv[2], encoding="utf-8"))}
    outs = []
    for raw in sys.argv[3:]:
        rows = [json.loads(l) for l in open(raw, encoding="utf-8")]
        for r in rows:
            r["ok"], r["kind"] = ok(tests[r["id"]], r["content"]), tests[r["id"]].get("kind", "fact")
        outs.append(raw.replace(".jsonl", ".scored.jsonl"))
        with open(outs[-1], "w", encoding="utf-8", newline="\n") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    report(outs)
else:
    tests = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
    out = sys.argv[2]
    done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
    lock = threading.Lock()

    def one(t):
        row = run(t)
        with lock, open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{row['id']}: {'ok' if row['ok'] else 'FAIL'} {row['done_reason']} {row['tokens']} tok {row['secs']} s", flush=True)

    with cf.ThreadPoolExecutor(2) as ex:
        list(ex.map(one, [t for t in tests if t["id"] not in done]))
    report([out])
