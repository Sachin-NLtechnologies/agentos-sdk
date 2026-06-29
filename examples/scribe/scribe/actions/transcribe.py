import base64, os, tempfile, urllib.request

def _materialize(payload):
    """Return a local audio path from url or base64."""
    if payload.get("audio_url"):
        fd, path = tempfile.mkstemp(suffix=".audio")
        os.close(fd)
        urllib.request.urlretrieve(payload["audio_url"], path)
        return path
    if payload.get("audio_b64"):
        fd, path = tempfile.mkstemp(suffix=".audio")
        with os.fdopen(fd, "wb") as f:
            f.write(base64.b64decode(payload["audio_b64"]))
        return path
    raise ValueError("provide audio_url or audio_b64")

def transcribe(payload):
    path = _materialize(payload)
    language = payload.get("language")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        # pattern still validates without the heavy model installed
        return ({"transcript": "(stub) install faster-whisper to enable real STT",
                 "segments": [], "language": language or "unknown"},
                {"audio_seconds": 0, "cost": 0.0, "engine": "stub"})
    model = WhisperModel(os.getenv("WHISPER_MODEL", "base"), device="cpu", compute_type="int8")
    segments, info = model.transcribe(path, language=language)
    segs = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    transcript = " ".join(s["text"].strip() for s in segs).strip()
    usage = {"audio_seconds": round(getattr(info, "duration", 0.0), 2), "cost": 0.0, "engine": "faster-whisper"}
    return {"transcript": transcript, "segments": segs, "language": info.language}, usage
