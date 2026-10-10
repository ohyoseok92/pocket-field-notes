"""A tiny local web app that turns spare time into an outdoor observation quest."""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parent
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b-instruct-q4_K_M")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")


def make_prompt(data: dict[str, str]) -> str:
    return f"""You are an offline-first outdoor activity designer. Create a short, concrete
observation quest that gets the person away from their screen. Never invent live
weather, opening hours, accessible routes, map facts, or local hazards. The person
chooses their own safe route. Avoid collecting personal data. The quest must work
without taking a photo or using the phone after reading it.

Available time: {data['minutes']} minutes
Setting: {data['setting']}
Activity preference: {data['pace']}
Interest: {data['interest']}

Return only a JSON object with these keys:
title (max 8 words), intro (one sentence), steps (array of exactly 3 objects,
each with minutes as integer, action as one sentence, and notice as one short
question), reflection (one question). Total step minutes must equal available
time. Ask about colors, sounds, or patterns in whatever is actually nearby.
Do not mention an entrance, path, bench, tree, flower, pond, stream, forest,
bird, leaf, or any other feature that might be absent. Use only general
phrases such as 'where you are' and 'your surroundings'."""


def generate_quest(data: dict[str, str]) -> dict:
    payload = json.dumps(
        {"model": MODEL, "prompt": make_prompt(data), "format": "json", "stream": False,
         "options": {"temperature": 0.55, "num_predict": 450}},
    ).encode("utf-8")
    req = request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=120) as resp:
        raw = json.load(resp)
    quest = json.loads(raw["response"])
    steps = quest.get("steps")
    if not isinstance(steps, list) or len(steps) != 3:
        raise ValueError("Model did not return three steps")
    for step in steps:
        if not isinstance(step, dict) or not isinstance(step.get("minutes"), int):
            raise ValueError("Invalid step duration")
        if not isinstance(step.get("action"), str) or not isinstance(step.get("notice"), str):
            raise ValueError("Invalid step text")
    for key in ("title", "intro", "reflection"):
        if not isinstance(quest.get(key), str):
            raise ValueError(f"Missing {key}")
    # The model supplies the observation ideas. Movement and timing stay
    # deterministic so it cannot invent a route or a local landmark.
    total = int(data["minutes"])
    durations = [total // 4, total // 2, total - (total // 4 + total // 2)]
    actions = (
        ["Walk at a comfortable pace on a route you choose.",
         "Pause somewhere safe and look around.",
         "Continue or return on a route you choose."]
        if data["pace"] == "gentle walk" else
        ["Settle in a place that feels safe and comfortable.",
         "Look and listen without moving around.",
         "Take one final slow look at your surroundings."]
    )
    fallback = {
        "color": ["What color stands out first?", "Which shade changes as you look longer?", "What color did you almost miss?"],
        "sound": ["Which sound is nearest?", "Which sound comes and goes?", "What is quieter than you expected?"],
        "patterns": ["What shape repeats?", "What pattern changes when you move?", "Which small detail breaks a pattern?"],
    }[data["interest"]]
    absent_feature = re.compile(r"\b(entrance|gate|bench|path|trail|tree|flower|pond|stream|river|forest|bird|leaf|leaves|lake|hill|mountain)\b", re.I)
    for index, step in enumerate(steps):
        step["minutes"] = durations[index]
        step["action"] = actions[index]
        if absent_feature.search(step["notice"]):
            step["notice"] = fallback[index]
    quest["intro"] = "Read this card once, choose your own safe place, then let the screen go."
    if absent_feature.search(quest["reflection"]):
        quest["reflection"] = "What did you notice outside that you would have missed on a screen?"
    return quest


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in ("/", "/app.js", "/style.css"):
            self.send_error(404)
            return
        name = "index.html" if self.path == "/" else self.path[1:]
        mime = "text/html" if name.endswith(".html") else "text/javascript" if name.endswith(".js") else "text/css"
        body = (ROOT / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/quest":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 2 or size > 4096:
                raise ValueError("Request must be between 2 and 4096 bytes")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
            minutes = int(data.get("minutes", 0))
            if minutes not in (10, 20, 30):
                raise ValueError("Choose 10, 20, or 30 minutes")
            cleaned = {"minutes": str(minutes)}
            for key, allowed in {
                "setting": {"city sidewalk", "park", "balcony or doorstep"},
                "pace": {"gentle walk", "sit and observe"},
                "interest": {"color", "sound", "patterns"},
            }.items():
                value = data.get(key)
                if value not in allowed:
                    raise ValueError(f"Invalid {key}")
                cleaned[key] = value
            quest = generate_quest(cleaned)
            self.reply(200, quest)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.reply(400, {"error": str(exc)})
        except (error.URLError, TimeoutError, KeyError) as exc:
            self.reply(503, {"error": f"Local model unavailable: {exc}"})

    def reply(self, code: int, body: dict) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    print(f"Pocket Field Notes: http://127.0.0.1:{port}  |  Ollama model: {MODEL}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
