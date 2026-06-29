def example(payload):
    text = payload.get("text", "")
    return {"output": {"echo": text}, "usage": {"tokens_in": len(text.split()), "cost": 0.0}}
