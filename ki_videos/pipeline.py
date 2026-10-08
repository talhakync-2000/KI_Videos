"""Verbindet alle Schritte: Skript, Bilder, Stimme, Video und Upload."""
import json
import re
from datetime import datetime
from pathlib import Path

import yaml

from . import images, render, script, upload, voice

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "niches.yaml"
OUTPUT = ROOT / "output"


def load_niches() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["niches"]


def _slug(text: str) -> str:
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:40]


def _history_file(niche_name: str) -> Path:
    return OUTPUT / niche_name / "history.json"


def _load_history(niche_name: str) -> list[str]:
    path = _history_file(niche_name)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _save_history(niche_name: str, titles: list[str]) -> None:
    path = _history_file(niche_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(titles, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_meta(folder: Path, meta: dict) -> None:
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def generate(niche_name: str, theme: str | None = None) -> Path:
    niche = load_niches()[niche_name]
    history = _load_history(niche_name)

    print(f"[{niche_name}] Skript wird geschrieben ...")
    data = script.generate_script(niche, theme, history)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = OUTPUT / niche_name / f"{stamp}-{_slug(data['title'])}"
    folder.mkdir(parents=True)
    (folder / "script.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    scenes = data["scenes"]
    image_paths = []
    for i, scene in enumerate(scenes):
        print(f"[{niche_name}] Bild {i + 1}/{len(scenes)} ...")
        image_paths.append(images.generate_image(scene["image_prompt"], folder / f"scene_{i:02d}.png"))

    print(f"[{niche_name}] Voiceover ...")
    scene_texts = [s["narration"].strip() for s in scenes]
    voice_path = folder / "voice.mp3"
    alignment = voice.generate_voice(" ".join(scene_texts), niche["voice_id"], voice_path)

    print(f"[{niche_name}] Video wird geschnitten ...")
    total = render.audio_duration(voice_path)
    durations = render.scene_durations(scene_texts, alignment, total)
    subs = folder / "subtitles.ass"
    render.write_subtitles(voice.words_from_alignment(alignment), subs)
    music = ROOT / niche["music"] if niche.get("music") else None
    video = render.render_video(image_paths, durations, voice_path, subs, folder / "video.mp4", music)

    hashtags = list(dict.fromkeys(niche.get("hashtags", []) + data["hashtags"]))
    _write_meta(folder, {
        "niche": niche_name,
        "status": "review",
        "title": data["title"],
        "description": f"{data['description']}\n\n{' '.join(hashtags)}",
        "video": video.name,
    })
    _save_history(niche_name, history + [data["title"]])
    print(f"[{niche_name}] Fertig: {video}")
    return folder


def upload_folder(folder: Path) -> dict:
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    if meta["status"] == "uploaded":
        raise RuntimeError(f"{folder} wurde schon hochgeladen")
    niche = load_niches()[meta["niche"]]

    result = upload.upload_video(
        folder / meta["video"], meta["title"], meta["description"],
        niche["upload_profile"], niche["platforms"],
    )
    meta["status"] = "uploaded"
    meta["uploaded_at"] = datetime.now().isoformat(timespec="seconds")
    meta["upload_result"] = result
    _write_meta(folder, meta)
    return result


def pending() -> list[Path]:
    return sorted(
        p.parent for p in OUTPUT.glob("*/*/meta.json")
        if json.loads(p.read_text(encoding="utf-8"))["status"] == "review"
    )
