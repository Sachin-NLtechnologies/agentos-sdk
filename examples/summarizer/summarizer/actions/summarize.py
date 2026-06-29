import re
from collections import Counter

_WORD = re.compile(r"[A-Za-z']+")
_STOP = set("the a an and or but of to in on for with at by from is are was were be been being this that these those it its as he she they we you i".split())

def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]

def summarize(text, max_sentences=3):
    text = (text or "").strip()
    if not text:
        return {"summary": "", "bullets": []}, {"tokens_in": 0, "tokens_out": 0, "cost": 0.0}
    sents = _sentences(text)
    words = [w.lower() for w in _WORD.findall(text)]
    freq = Counter(w for w in words if w not in _STOP and len(w) > 2)
    def score(s):
        sw = [w.lower() for w in _WORD.findall(s)]
        return sum(freq.get(w, 0) for w in sw) / (len(sw) or 1)
    ranked = sorted(sents, key=score, reverse=True)[:max(1, max_sentences)]
    # keep original order
    chosen = [s for s in sents if s in ranked][:max_sentences]
    summary = " ".join(chosen)
    bullets = chosen
    usage = {"tokens_in": len(words), "tokens_out": len(_WORD.findall(summary)), "cost": 0.0}
    return {"summary": summary, "bullets": bullets}, usage
