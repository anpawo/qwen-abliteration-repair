"""MATH-500 against an Ollama model. Resume-safe: problems already in the output JSONL are skipped.

usage: OLLAMA_URL=http://host:11434 python3 -I -u eval.py DATA.jsonl OUT.jsonl --model NAME --think off|on [--sample 150] [--limit 5]
       python3 -I eval.py --test
"""
import argparse, concurrent.futures, json, math, os, random, re, subprocess, sys, threading, time, urllib.request

STALL = 300
LOCK = threading.Lock()
CHECK = 300  # every CHECK s of generation, a judge reads the partial work; STUCK ends the problem as wrong
JUDGE = """A model is solving the math problem below and has not finished. Its partial work follows.
Answer STUCK only if it is going in circles: redoing the same derivation, flipping between the same answers, or repeating a contradiction without a new idea. Answer OK if it is still making progress, even slowly or while fixing its own mistakes.
Reply with one word: OK or STUCK.

Problem:
{problem}

Partial work (its last part):
{work}"""
PROMPT = "{problem}\nPlease reason step by step, and put your final answer within \\boxed{{}}."  # MIT's / Qwen's
SAMPLING = {  # Qwen3.5 model-card settings, as in MIT's evaluate.py (think35 / nothink35)
    "on": {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5, "num_ctx": 32768, "num_predict": 30000},
    "off": {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "presence_penalty": 1.5, "num_ctx": 8192, "num_predict": 7000},
}


def last_boxed(text):
    i = max(text.rfind("\\boxed"), text.rfind("\\fbox"))
    if i < 0:
        return None
    j = text.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j + 1:k]
    return None


def strip_cmd(s, cmd):
    """\\cmd{x} -> x, braces balanced."""
    while (i := s.find(cmd + "{")) >= 0:
        j, depth = i + len(cmd), 0
        for k in range(j, len(s)):
            depth += {"{": 1, "}": -1}.get(s[k], 0)
            if depth == 0:
                s = s[:i] + s[j + 1:k] + s[k + 1:]
                break
        else:
            break
    return s


def norm(s):
    s = s.strip()
    for c in ("\\text", "\\textbf", "\\mathrm", "\\mbox", "\\mathbf"):
        s = strip_cmd(s, c)
    s = re.sub(r"\\left|\\right|\\!|\\,|\\;|\\:|\\ |\\displaystyle|\\\$|\$", "", s)
    s = s.replace("dfrac", "frac").replace("tfrac", "frac").replace("^\\circ", "").replace("^{\\circ}", "").replace("°", "")
    s = re.sub(r"\\(degrees?)|(?<![a-z])(degrees?|units?|cm|inches|meters)$", "", s)
    s = re.sub(r"^[a-zA-Z]\s*=\s*", "", s)  # "x = 5" -> "5"
    s = s.replace(" ", "").rstrip(".")
    s = re.sub(r"(\d),(\d{3})(?!\d)", r"\1\2", s)  # 1,000 -> 1000
    s = re.sub(r"(\d+)\.0+(?!\d)", r"\1", s)
    s = re.sub(r"\\frac(\d)(\d)", r"\\frac{\1}{\2}", s)
    s = re.sub(r"\\frac\{([^{}]*)\}(\d)", r"\\frac{\1}{\2}", s)
    s = re.sub(r"\\sqrt(\d)", r"\\sqrt{\1}", s)
    return s


def to_sympy(s):
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    t = s
    for _ in range(5):
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", t)
        t = re.sub(r"\\sqrt\[([^{}]*)\]\{([^{}]*)\}", r"((\2)**(1/(\1)))", t)
        t = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", t)
    t = t.replace("\\pi", "pi").replace("\\cdot", "*").replace("\\times", "*").replace("^", "**").replace("{", "(").replace("}", ")")
    t = t.replace("\\infty", "oo").replace("%", "")
    if "\\" in t or "=" in t or not t:
        return None
    return parse_expr(t, transformations=standard_transformations + (implicit_multiplication_application,), evaluate=True)


def split_top(s):
    """'(1,2),3' -> ['(1,2)','3'] for tuples / lists of answers."""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += ch in "([{" ; depth -= ch in ")]}"
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    return out + [cur]


def equal(pred, gold):
    if pred is None:
        return False
    a, b = norm(pred), norm(gold)
    if a == b:
        return True
    pa, pb = split_top(a.strip("()[]") if a[:1] in "([" and a[-1:] in ")]" else a), split_top(b.strip("()[]") if b[:1] in "([" and b[-1:] in ")]" else b)
    if len(pa) != len(pb):
        return False
    if len(pa) > 1:
        if (a[:1] in "([") != (b[:1] in "(["):
            return False
        ordered = all(equal(x, y) for x, y in zip(pa, pb))
        return ordered or (a[:1] not in "([" and sorted(map(norm, pa)) == sorted(map(norm, pb)))  # bare lists: any order
    try:
        import sympy
        x, y = to_sympy(a), to_sympy(b)
        if x is None or y is None:
            return False
        d = sympy.simplify(x - y)
        return d == 0 or (d.is_number and abs(complex(d)) < 1e-6 * max(1, abs(complex(y))))
    except Exception:
        return False


def test():
    assert last_boxed("a \\boxed{\\frac{1}{2}} b \\boxed{3}") == "3"
    assert last_boxed("x \\boxed{\\left( 3, \\frac{\\pi}{2} \\right)}") == "\\left( 3, \\frac{\\pi}{2} \\right)"
    assert last_boxed("no box") is None
    assert equal("\\left( 3, \\frac{\\pi}{2} \\right)", "\\left( 3, \\frac{\\pi}{2} \\right)")
    assert equal("\\dfrac{14}{3}", "\\frac{14}{3}")
    assert equal("4.0", "4")
    assert equal("90^\\circ", "90")
    assert equal("\\text{Evelyn}", "\\text{Evelyn}")
    assert equal("\\frac12", "\\frac{1}{2}")
    assert equal("0.5", "\\frac{1}{2}")
    assert equal("2\\sqrt{2}", "\\sqrt{8}")
    assert equal("x=5", "5")
    assert equal("10,000", "10000")
    assert equal("(3,\\frac{\\pi}{2})", "\\left( 3, \\frac{\\pi}{2} \\right)")
    assert not equal("3", "4")
    assert not equal("(1,2)", "(2,1)")
    assert not equal(None, "1")
    assert not equal("\\frac{1}{3}", "\\frac{1}{2}")
    print("ok")


def ask_openai(model, problem, think):
    """An OpenAI-compatible server (vLLM): one blocking request, no loop check (the cap ends loops)."""
    s = SAMPLING[think]
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT.format(problem=problem)}],
            "max_tokens": s["num_predict"], "seed": 0, **{k: s[k] for k in ("temperature", "top_p", "top_k", "presence_penalty")},
            "chat_template_kwargs": {"enable_thinking": think == "on"}}
    req = urllib.request.Request(os.environ["OPENAI_URL"].rstrip("/") + "/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=7200))
    ch = r["choices"][0]
    return {"model": model, "message": {"content": ch["message"].get("content") or "", "thinking": ch["message"].get("reasoning_content") or ""},
            "eval_count": r["usage"]["completion_tokens"], "prompt_eval_count": r["usage"]["prompt_tokens"],
            "done_reason": ch["finish_reason"]}


def ask(model, problem, think):
    if os.environ.get("OPENAI_URL"):
        return ask_openai(model, problem, think)
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/chat"
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT.format(problem=problem)}], "stream": True,
            "think": think == "on", "keep_alive": "30m", "options": {**SAMPLING[think], "seed": 0}}
    t0, parts, due = time.time(), [], [CHECK]

    def on_line(line):
        m = json.loads(line).get("message", {}) if line.strip() else {}
        parts.append((m.get("thinking") or "") + (m.get("content") or ""))
        if time.time() - t0 >= due[0]:
            due[0] += CHECK
            if judge(problem, "".join(parts), time.time() - t0) == "STUCK":
                raise Stuck

    # Streamed so a stalled request (no token for STALL s) aborts and retries, while long answers still finish.
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    lines = []
    try:
        with urllib.request.urlopen(req, timeout=STALL) as r:
            for raw in r:
                line = raw.decode()
                lines.append(line)
                on_line(line)
    except Stuck:
        return {"model": model, "message": {"content": "".join(parts)}, "eval_count": len(parts), "done_reason": "stuck"}
    return merge("".join(lines))


class Stuck(Exception):
    pass


def judge(problem, work, secs):
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", "--setting-sources", "", "--tools", "",
                            "--strict-mcp-config", "--no-session-persistence"], input=JUDGE.format(problem=problem, work=work[-12000:]),
                           capture_output=True, text=True, timeout=180, env=env, cwd="/tmp")
        v = "STUCK" if r.stdout.strip().upper().startswith("STUCK") else "OK"
    except Exception as e:  # a failed judge never ends a problem
        v = f"OK (judge failed: {e})"[:120]
    print(f"  judge at {secs:.0f}s, {len(work)} chars: {v}", flush=True)
    return v


def merge(out):
    chunks = [json.loads(l) for l in out.splitlines() if l.strip()]
    if not chunks or not chunks[-1].get("done"):
        raise RuntimeError("stream ended before done")
    d = chunks[-1]
    d["message"] = {k: "".join(c.get("message", {}).get(k) or "" for c in chunks) for k in ("content", "thinking")}
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--model", default="qwen3.5-9b-abl")
    ap.add_argument("--think", choices=["on", "off"], default="off")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--score", action="store_true", help="print accuracy of OUT (first positional) and exit")
    a = ap.parse_args()
    if a.test:
        return test()
    if a.score:
        rs = [json.loads(l) for l in open(a.data)]
        n, k = len(rs), sum(r["correct"] for r in rs)
        p, z = k / n, 1.96
        c, h = (p + z * z / (2 * n)) / (1 + z * z / n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        cut = sum(r["done_reason"] == "length" for r in rs)
        print(f"n={n} correct={k} acc={p:.1%} wilson95=[{c - h:.1%}, {c + h:.1%}] avg_s={sum(r['seconds'] for r in rs) / n:.0f} "
              f"avg_tokens={sum(r['eval_count'] or 0 for r in rs) / n:.0f} hit_length={cut} stuck={sum(r["done_reason"] == "stuck" for r in rs)} no_boxed={sum(r['pred'] is None for r in rs)}")
        return
    model = a.model
    rows = [json.loads(l) for l in open(a.data)]
    order = random.Random(0).sample(range(len(rows)), a.sample) if a.sample else list(range(len(rows)))
    done = set()
    try:
        done = {json.loads(l)["unique_id"] for l in open(a.out)}
    except FileNotFoundError:
        pass
    todo = [i for i in order if rows[i]["unique_id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"model={model} think={a.think} planned={len(order)} done={len(done)} now={len(todo)}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get("CONC", 1))) as ex:
        list(ex.map(lambda i: one(a, model, rows[i], i), todo))


def one(a, model, r, i):
    for attempt in range(4):
        try:
            t0 = time.time()
            d = ask(model, r["problem"], a.think)
            break
        except Exception as e:
            print(f"{r['unique_id']} attempt {attempt}: {e}", flush=True)
            if attempt == 3:
                raise
            time.sleep(150)
    secs = time.time() - t0
    msg = d.get("message", {})
    text = msg.get("content", "")
    pred = last_boxed(text)
    rec = {"idx": i, "unique_id": r["unique_id"], "level": r["level"], "subject": r["subject"], "gold": r["answer"],
           "pred": pred, "correct": equal(pred, r["answer"]), "seconds": round(secs, 1), "model": d.get("model"),
           "think": a.think, "eval_count": d.get("eval_count"), "prompt_eval_count": d.get("prompt_eval_count"),
           "done_reason": d.get("done_reason"), "thinking_chars": len(msg.get("thinking") or ""), "response": text}
    with LOCK, open(a.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"{r['unique_id']} correct={rec['correct']} s={rec['seconds']} tok={rec['eval_count']} {rec['done_reason']}", flush=True)


if __name__ == "__main__":
    main()
