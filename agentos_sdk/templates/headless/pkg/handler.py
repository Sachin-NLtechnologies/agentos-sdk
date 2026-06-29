from .actions.example import example
def dispatch(action, payload):
    action = (action or "").upper()
    if action == "EXAMPLE":
        return example(payload)
    raise ValueError(f"unknown action: {action}")
