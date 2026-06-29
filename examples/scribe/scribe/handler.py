from .actions.transcribe import transcribe

def dispatch(action, payload):
    action = (action or "").upper()
    if action == "TRANSCRIBE":
        out, usage = transcribe(payload)
        return {"output": out, "usage": usage}
    raise ValueError(f"unknown action: {action}")
