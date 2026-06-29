from .actions.summarize import summarize

def dispatch(action, payload):
    action = (action or "").upper()
    if action == "SUMMARIZE":
        out, usage = summarize(payload.get("text", ""), int(payload.get("max_sentences", 3)))
        return {"output": out, "usage": usage}
    raise ValueError(f"unknown action: {action}")
