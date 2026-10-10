"""Render a short, truthful walkthrough using the saved live app response."""

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "demo-response.json").read_text(encoding="utf-8-sig"))
OUT = ROOT / "demo-frames"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/segoeui.ttf"
BOLD = "C:/Windows/Fonts/segoeuib.ttf"


def f(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def base(number, eyebrow, title, subtitle):
    image = Image.new("RGB", (1280, 720), "#eef1e5")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((32, 28, 1248, 692), radius=28, fill="#fafbf4")
    d.rounded_rectangle((64, 54, 1216, 118), radius=18, fill="#193b32")
    d.text((86, 69), "POCKET FIELD NOTES", font=f(22, True), fill="#eaf2d8")
    d.text((950, 72), "TOUCH GRASS / 2026", font=f(15, True), fill="#eaf2d8")
    d.text((72, 154), eyebrow.upper(), font=f(18, True), fill="#697863")
    d.text((72, 191), title, font=f(49, True), fill="#193b32")
    d.text((73, 260), subtitle, font=f(23), fill="#576456")
    d.text((73, 652), f"{number:02d} / 04", font=f(16, True), fill="#849582")
    d.text((1003, 652), "LOCAL AI  /  NO GPS", font=f(16, True), fill="#849582")
    return image, d


im, d = base(1, "Make a small plan", "Go outside. Notice more.", "Choose four simple inputs. No sign-in, GPS, or cloud prompt.")
for i, (label, value) in enumerate(
    [("TIME", "20 minutes"), ("SETTING", "Park"), ("PACE", "Gentle walk"), ("INTEREST", "Color")]
):
    x = 72 + (i % 2) * 580
    y = 347 + (i // 2) * 122
    d.rounded_rectangle((x, y, x + 545, y + 98), radius=18, fill="#e5ead8")
    d.text((x + 25, y + 18), label, font=f(15, True), fill="#65795c")
    d.text((x + 25, y + 46), value, font=f(27, True), fill="#193b32")
im.save(OUT / "slide-01.png")

im, d = base(2, "Local inference", "One prompt. A personal field card.", "The app calls Ollama on localhost, then applies clear guardrails.")
for i, (head, desc) in enumerate(
    [("01", "Your four choices"), ("02", "Open-weight Qwen model"), ("03", "Safe, timed activity")]
):
    x = 72 + i * 385
    d.rounded_rectangle((x, 370, x + 353, 535), radius=20, fill="#e5ead8")
    d.text((x + 24, 394), head, font=f(42, True), fill="#6e8a58")
    d.text((x + 24, 473), desc, font=f(20, True), fill="#193b32")
im.save(OUT / "slide-02.png")

im, d = base(3, "Live result", DATA["title"], DATA["intro"])
for i, step in enumerate(DATA["steps"]):
    y = 330 + i * 96
    d.rounded_rectangle((72, y, 1208, y + 82), radius=17, fill="#e5ead8")
    d.text((93, y + 14), f"{step['minutes']} MIN", font=f(20, True), fill="#668153")
    d.text((235, y + 9), step["action"], font=f(21, True), fill="#193b32")
    d.text((235, y + 42), step["notice"], font=f(18), fill="#566753")
im.save(OUT / "slide-03.png")

im, d = base(4, "Take the card with you", "Close the screen. Touch grass.", "Print the card and follow a route that is safe for you.")
d.rounded_rectangle((72, 352, 1208, 545), radius=22, fill="#dfe9cf")
d.text((102, 376), "REFLECT WHEN YOU RETURN", font=f(18, True), fill="#648052")
d.text((102, 427), DATA["reflection"], font=f(27, True), fill="#193b32")
d.text((102, 503), "MIT licensed  •  Python standard library  •  Ollama + Qwen2.5-Coder", font=f(17), fill="#61715c")
im.save(OUT / "slide-04.png")

cover = Image.new("RGB", (1000, 420), "#193b32")
cd = ImageDraw.Draw(cover)
cd.rounded_rectangle((35, 35, 965, 385), radius=28, fill="#e9efda")
cd.text((76, 73), "POCKET FIELD NOTES", font=f(23, True), fill="#648052")
cd.text((76, 134), "A small field card", font=f(54, True), fill="#193b32")
cd.text((76, 202), "for a bigger world.", font=f(54, True), fill="#193b32")
cd.text((77, 313), "LOCAL OPEN-WEIGHT AI   •   PRINT IT   •   GO OUTSIDE", font=f(19, True), fill="#647957")
cover.save(ROOT / "cover.png")

subprocess.run(
    [
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", "1/5", "-i",
        str(OUT / "slide-%02d.png"), "-vf", "fps=24,format=yuv420p", "-c:v",
        "libx264", "-movflags", "+faststart", str(ROOT / "demo.mp4"),
    ],
    check=True,
)
print(ROOT / "demo.mp4")
