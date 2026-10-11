"""Verbindet alle Schritte: Skript, Bilder, Stimme, Video und Upload."""
import json
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import images, render, script, upload, voice

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "niches.yaml"
OUTPUT = ROOT / "output"


def load_niches() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["niches"]


def active_niches() -> list[str]:
    """Aktive Kanäle, die aus Skripten erzeugt werden (Clip-Kanäle laufen über `clips`)."""
    return [name for name, n in load_niches().items()
            if n.get("active", True) and n.get("mode") != "clip"]


def _slug(text: str) -> str:
    text = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:40]


def _history_file(niche_name: str) -> Path:
    return OUTPUT / niche_name / "history.json"


def _load_history(niche_name: str) -> list[dict]:
    path = _history_file(niche_name)
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8"))
    # ältere Version speicherte nur Titel als Strings
    return [e if isinstance(e, dict) else {"title": e, "summary": e} for e in entries]


def _save_history(niche_name: str, entries: list[dict]) -> None:
    path = _history_file(niche_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_meta(folder: Path, meta: dict) -> None:
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_from_images(niche: dict, name: str, scenes: list[dict], folder: Path, music: Path | None) -> Path:
    image_paths = []
    for i, scene in enumerate(scenes):
        print(f"[{name}] Bild {i + 1}/{len(scenes)} ...")
        image_paths.append(images.generate_image(
            scene["visual_prompt"], folder / f"scene_{i:02d}.png", niche.get("image_model")))

    print(f"[{name}] Voiceover ...")
    scene_texts = [s["narration"].strip() for s in scenes]
    voice_path = folder / "voice.mp3"
    alignment = voice.generate_voice(" ".join(scene_texts), niche["voice_id"], voice_path)

    print(f"[{name}] Video wird geschnitten ...")
    total = render.audio_duration(voice_path)
    durations = render.scene_durations(scene_texts, alignment, total)
    # TikTok Creator Rewards zählt nur Videos ab 60 s: notfalls das letzte Bild länger zeigen
    length = max(total + 0.5, float(niche.get("min_duration", 0)))
    durations[-1] += length - sum(durations)
    subs = folder / "subtitles.ass"
    render.write_subtitles(voice.words_from_alignment(alignment), subs, niche.get("subtitle_color", "#FFFFFF"))
    return render.render_video(image_paths, durations, voice_path, subs, folder / "video.mp4", music, length)


def _build_from_clips(niche: dict, name: str, scenes: list[dict], folder: Path, music: Path | None) -> Path:
    clips = []
    for i, scene in enumerate(scenes):
        print(f"[{name}] Videoclip {i + 1}/{len(scenes)} (dauert etwas) ...")
        clips.append(images.generate_clip(
            scene["visual_prompt"], folder / f"clip_{i:02d}.mp4", niche.get("video_model")))
    print(f"[{name}] Clips werden zusammengeschnitten ...")
    return render.concat_clips(clips, folder / "video.mp4", music)


def load_script_file(path: Path) -> dict:
    """Lädt ein fertiges Skript (z. B. aus content/) im selben Format, das Claude erzeugt."""
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in script.SCHEMA["required"] if k not in data]
    if missing:
        raise ValueError(f"{path}: es fehlen die Felder {', '.join(missing)}")
    for i, scene in enumerate(data["scenes"]):
        if "visual_prompt" not in scene or "narration" not in scene:
            raise ValueError(f"{path}: Szene {i + 1} braucht 'narration' und 'visual_prompt'")
    return data


def generate(niche_name: str, theme: str | None = None, script_file: Path | None = None) -> Path:
    niche = load_niches()[niche_name]
    history = _load_history(niche_name)

    if script_file:
        print(f"[{niche_name}] Skript aus {script_file} ...")
        data = load_script_file(script_file)
    else:
        print(f"[{niche_name}] Skript wird geschrieben ...")
        data = script.generate_script(niche, theme, history)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = OUTPUT / niche_name / f"{stamp}-{_slug(data['title'])}"
    folder.mkdir(parents=True)
    (folder / "script.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    music = ROOT / niche["music"] if niche.get("music") else None
    build = _build_from_clips if niche.get("mode") == "video" else _build_from_images
    video = build(niche, niche_name, data["scenes"], folder, music)

    hashtags = list(dict.fromkeys(niche.get("hashtags", []) + data["hashtags"]))
    _write_meta(folder, {
        "niche": niche_name,
        "status": "review",
        "title": data["title"],
        "summary": data["episode_summary"],
        "description": f"{data['description']}\n\n{' '.join(hashtags)}",
        "hashtags": hashtags,
        "video": video.name,
    })
    _save_history(niche_name, history + [{"title": data["title"], "summary": data["episode_summary"]}])
    print(f"[{niche_name}] Fertig: {video}")
    return folder


def upload_folder(folder: Path) -> dict:
    """Schickt ein Video an Upload-Post.

    - Liegt der geplante Slot noch in der Zukunft, plant Upload-Post den Post selbst ein
      (der PC muss zur Posting-Zeit nicht laufen).
    - Status "partial": nur die Plattformen, die beim letzten Mal fehlgeschlagen sind.
    """
    meta = _read_meta(folder)
    if meta["status"] == "uploaded":
        raise RuntimeError(f"{folder} wurde schon hochgeladen")
    niche = load_niches()[meta["niche"]]
    platforms = meta["failed_platforms"] if meta["status"] == "partial" else niche["platforms"]

    publish_at = None
    if meta.get("scheduled_at"):
        planned = datetime.fromisoformat(meta["scheduled_at"])
        if planned > datetime.now().astimezone() + timedelta(minutes=2):
            publish_at = planned

    fields = upload.build_fields(meta, niche, platforms, publish_at)
    key = f"{meta['niche']}-{folder.name}-{'-'.join(sorted(platforms))}"[:255]
    result = upload.upload_video(folder / meta["video"], fields, key)

    failed = upload.failed_platforms(result)
    meta["status"] = "partial" if failed else "uploaded"
    meta["failed_platforms"] = failed
    meta["uploaded_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    meta.setdefault("upload_results", []).append(result)
    _write_meta(folder, meta)
    return result


def discard(folder: Path) -> None:
    """Löscht ein nicht hochgeladenes Video und nimmt es aus der Historie."""
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    if meta["status"] == "uploaded":
        raise RuntimeError(f"{folder} ist schon online und kann nicht verworfen werden")
    if meta["status"] == "partial":
        raise RuntimeError(f"{folder} ist auf einigen Plattformen schon online und kann nicht verworfen werden")
    history = [h for h in _load_history(meta["niche"]) if h["title"] != meta["title"]]
    _save_history(meta["niche"], history)
    shutil.rmtree(folder)


def _read_meta(folder: Path) -> dict:
    return json.loads((folder / "meta.json").read_text(encoding="utf-8"))


def by_status(status: str) -> list[Path]:
    return sorted(p.parent for p in OUTPUT.glob("*/*/meta.json") if _read_meta(p.parent)["status"] == status)


def pending() -> list[Path]:
    return by_status("review")


def _next_free_slot(niche_name: str, niche: dict) -> datetime:
    tz = ZoneInfo(niche.get("timezone", "Europe/Berlin"))
    times = sorted(niche.get("posting_times") or ["19:00"])
    taken = {
        datetime.fromisoformat(m["scheduled_at"])
        for m in (_read_meta(p.parent) for p in OUTPUT.glob(f"{niche_name}/*/meta.json"))
        if m.get("scheduled_at") and m["status"] in ("scheduled", "uploaded", "partial")
    }
    # mindestens 20 Minuten Vorlauf, damit Upload und Verarbeitung vor dem Slot fertig sind
    earliest = datetime.now(tz) + timedelta(minutes=20)
    day = earliest.date()
    while True:
        for t in times:
            hour, minute = map(int, t.split(":"))
            slot = datetime(day.year, day.month, day.day, hour, minute, tzinfo=tz)
            if slot >= earliest and slot not in taken:
                return slot
        day += timedelta(days=1)


def schedule(folder: Path, push: bool = True) -> tuple[datetime, str | None]:
    """Gibt ein geprüftes Video frei und legt es auf den nächsten freien Posting-Slot.

    push=True: sofort an Upload-Post schicken, das den Post zum Slot veröffentlicht.
    Klappt das nicht (kein Netz, Key fehlt), bleibt es lokal geplant und der Upload-Job
    (hochladen --faellige) lädt es zur Posting-Zeit hoch. Rückgabe: (Slot, Fehlertext oder None).
    """
    meta = _read_meta(folder)
    if meta["status"] != "review":
        raise RuntimeError(f"{folder} hat Status '{meta['status']}', freigeben geht nur bei 'review'")
    slot = _next_free_slot(meta["niche"], load_niches()[meta["niche"]])
    meta["status"] = "scheduled"
    meta["scheduled_at"] = slot.isoformat(timespec="minutes")
    _write_meta(folder, meta)
    if not push:
        return slot, None
    try:
        upload_folder(folder)
        return slot, None
    except Exception as e:  # lokal geplant lassen, der Upload-Job holt es nach
        return slot, str(e)


def planned() -> list[tuple[datetime, Path, str]]:
    """Alles, was noch veröffentlicht wird: (Zeitpunkt, Ordner, 'Upload-Post' oder 'lokal')."""
    now = datetime.now().astimezone()
    out = []
    for p in OUTPUT.glob("*/*/meta.json"):
        m = _read_meta(p.parent)
        if not m.get("scheduled_at"):
            continue
        when = datetime.fromisoformat(m["scheduled_at"])
        if m["status"] == "scheduled":
            out.append((when, p.parent, "lokal"))
        elif m["status"] in ("uploaded", "partial") and when > now:
            out.append((when, p.parent, "Upload-Post"))
    return sorted(out)


def due() -> list[Path]:
    """Freigegebene Videos, deren Upload-Zeit erreicht ist."""
    now = datetime.now().astimezone()
    return [f for f in by_status("scheduled") if datetime.fromisoformat(_read_meta(f)["scheduled_at"]) <= now]
