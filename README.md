# Pocket Field Notes

A small, local web app for the 2026 Hacktoberfest Open-Source AI Challenge Week 1 theme, **Touch Grass**. It generates a three-step outdoor observation card and then asks you to close the screen. Users choose their own safe route; it never claims to know current weather, opening hours, or hazards.

## Run

Install [Ollama](https://ollama.com/) and pull the open-weight model:

```text
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
python server.py
```

Open <http://127.0.0.1:8765>. Python 3.11+ is the only runtime dependency. Set `OLLAMA_MODEL` to another locally installed model if desired. The interface makes no cloud inference calls; the optional Google Fonts stylesheet is only decorative, and system fonts work offline.

## Why open AI

The model generates observation questions from four constrained user choices, making the outdoor activity specific without sending a location or preference to a hosted model. Deterministic guardrails set the timing and movement, and replace questions that assume an unverified local landmark. Ollama serves inference on localhost; the app uses only Python standard library HTTP. Qwen2.5-Coder is an open-weight model from Qwen. No API key, paid service, account, tracking, or GPS is required. The generated card can be printed for a completely screen-free outing.

## Disclosure and limits

Codex helped draft, debug, and document this new project during the October 5–11, 2026 challenge window. The repo contains original app code; Ollama and Qwen2.5-Coder are credited dependencies. Model text can be imperfect. The app deliberately does not supply routes or real-time safety information. Test outdoors only when conditions and access are safe for you.

## Demo

Choose 20 minutes, Park, Gentle walk, and Color, then click **Make my field card**. A local Qwen model returns three steps and a reflection prompt. Use **Print card** to take it outside.

[`demo.mp4`](demo.mp4) is a 20-second captioned walkthrough. Its field card comes from a real local run, preserved in [`demo-response.json`](demo-response.json). The video uses rendered slides, not a screen recording. Run `python make_demo.py` with Pillow and FFmpeg to regenerate it.

## License

MIT, see `LICENSE`.
