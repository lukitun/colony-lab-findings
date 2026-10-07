"""Shared helper: one chat call to a chat-completions endpoint. Standard library only.
Configure with LLM_CHAT_URL and LLM_API_KEY. The key is read from the environment and never logged."""
import json, os, re, time, urllib.request, urllib.error

URL = os.environ.get("LLM_CHAT_URL", "")
KEY = os.environ.get("LLM_API_KEY", "")
THINK = re.compile(r"<think>.*?</think>", re.S)

def chat(model, messages, max_tokens=1200, temperature=0.7, timeout=150, retries=2):
    assert URL and KEY, "set LLM_CHAT_URL and LLM_API_KEY"
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens,
                       "temperature": temperature}).encode()
    err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(URL, data=body, headers={
            "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = json.loads(r.read())
            ch = (b.get("choices") or [{}])[0]
            msg = ch.get("message", {}) or {}
            text = THINK.sub("", msg.get("content") or "").strip()
            reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
            return dict(ok=bool(text), text=text, finish=ch.get("finish_reason"), usage=b.get("usage"),
                        reasoning_len=len(reasoning), elapsed=round(time.time() - t0, 2), err=None)
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:
            err = "timeout" if time.time() - t0 >= timeout - 1 else f"conn: {str(e)[:60]}"
            if err == "timeout":
                break
        time.sleep(6 * (attempt + 1))
    return dict(ok=False, text="", finish=None, usage=None, reasoning_len=0,
                elapsed=round(time.time() - t0, 2), err=err)

def log(path, rec):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
