"""GSM8K through the PC's ollama: accuracy and how often the answer runs out of tokens.

usage: python eval.py <model> <split> <start> <count> <out.jsonl>
Resumable: problems already in out.jsonl are skipped.
"""
import json, os, re, sys, time, urllib.request

MODEL, SPLIT, START, COUNT, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
HERE = os.path.dirname(os.path.abspath(__file__))
NUM_PREDICT = int(os.environ.get("NUM_PREDICT", 6144))
PROMPT = "{q}\nPlease reason step by step, and put your final answer within \\boxed{{}}."


LLAMA_PORT = os.environ.get("LLAMA_PORT")  # set: ask llama-server on that port instead of ollama


def post(url, body):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=7200))


def ask(q):
    """-> thinking, content, done_reason ('length' = hit the cap), tokens"""
    messages = [{"role": "user", "content": PROMPT.format(q=q)}]
    if LLAMA_PORT:
        # same sampling as the ollama Modelfile unless overridden
        r = post(f"http://127.0.0.1:{LLAMA_PORT}/v1/chat/completions", {
            "messages": messages, "max_tokens": NUM_PREDICT, "seed": 0, "top_k": 20, "top_p": 0.95,
            "temperature": float(os.environ.get("SAMPLE_TEMP", 1.0)),
            "presence_penalty": float(os.environ.get("SAMPLE_PRESENCE", 1.5)),
            "chat_template_kwargs": {"enable_thinking": True}})
        c = r["choices"][0]
        return (c["message"].get("reasoning_content") or "", c["message"].get("content") or "",
                c["finish_reason"], r["usage"]["completion_tokens"])
    r = post("http://127.0.0.1:11434/api/chat", {
        "model": MODEL, "stream": False, "think": True, "messages": messages,
        "options": {"num_ctx": 8192, "num_predict": NUM_PREDICT, "seed": 0}})
    return r["message"].get("thinking", ""), r["message"].get("content", ""), r.get("done_reason"), r.get("eval_count", 0)


def to_num(s):
    s = s.replace(",", "").replace("$", "")
    m = re.findall(r"-?\d+(?:\.\d+)?", s)
    return float(m[-1]) if m else None


def pred(content):
    boxed = re.findall(r"\\boxed\{([^{}]*)\}", content)
    return to_num(boxed[-1] if boxed else content)


def summary(rows):
    n = len(rows)
    ok = sum(r["correct"] for r in rows)
    cap = sum(r["done_reason"] == "length" for r in rows)
    print(f"{MODEL} {SPLIT}[{START}:{START + COUNT}] n={n} accuracy={ok}/{n} ({100 * ok / max(n, 1):.1f}%) "
          f"hit_cap={cap}/{n} ({100 * cap / max(n, 1):.1f}%) mean_tokens={sum(r['tokens'] for r in rows) / max(n, 1):.0f}")


assert to_num("$1,234.50") == 1234.5 and pred("so \\boxed{18}") == 18 and pred("answer is 7 apples") == 7

probs = [json.loads(l) for l in open(os.path.join(HERE, f"gsm8k_{SPLIT}.jsonl"), encoding="utf-8")][START:START + COUNT]
done = {}
if os.path.exists(OUT):
    for l in open(OUT, encoding="utf-8"):
        r = json.loads(l)
        done[r["i"]] = r
with open(OUT, "a", encoding="utf-8") as f:
    for k, p in enumerate(probs):
        i = START + k
        if i in done:
            continue
        t = time.time()
        thinking, content, reason, tokens = ask(p["question"])
        gold = to_num(p["answer"].split("####")[-1])
        got = pred(content)
        row = {"i": i, "gold": gold, "pred": got, "correct": got is not None and abs(got - gold) < 1e-6,
               "done_reason": reason, "tokens": tokens,
               "secs": round(time.time() - t, 1), "thinking": thinking, "content": content}
        f.write(json.dumps(row) + "\n")
        f.flush()
        done[i] = row
        print(i, row["correct"], row["done_reason"], row["tokens"], row["secs"], flush=True)
summary(list(done.values()))
