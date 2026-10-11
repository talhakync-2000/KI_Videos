"""Clip-Modus: aus langen Videos (Streams, Podcasts) automatisch Kurzclips schneiden.

Nur für Material, das du nutzen darfst, z. B. aus offiziellen Clipping-Kampagnen
(Whop Content Rewards, Ssemble) oder eigene Videos.

Ablauf: laden -> transkribieren (faster-whisper) -> Highlights auswählen (Claude-API oder
Claude Code über den Skill clip-auswahl, sonst einfache Heuristik) -> 9:16 schneiden mit
Untertiteln, optional Gameplay im unteren Bildschirmteil -> Ordner in output/<nische>/ zur Prüfung.
"""
import json
import random
import re
import subprocess
from datetime import datetime
from pathlib import Path

from . import pipeline, render

WORK = pipeline.ROOT / "work"
H_HALF = render.H // 2

AUSWAHL_SCHEMA = {
    "type": "object",
    "properties": {
        "clips": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number", "description": "Start in Sekunden"},
                    "end": {"type": "number", "description": "Ende in Sekunden"},
                    "title": {"type": "string", "description": "Viraler Titel, max. 80 Zeichen"},
                    "description": {"type": "string", "description": "1-2 Sätze Caption"},
                    "hashtags": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string", "description": "Warum dieser Moment funktioniert"},
                },
                "required": ["start", "end", "title", "description", "hashtags", "reason"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["clips"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------- Laden

def _probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(out.stdout)
    stream = data["streams"][0]
    return {"width": stream["width"], "height": stream["height"], "duration": float(data["format"]["duration"])}


def prepare(source: str, niche_name: str) -> Path:
    """Legt einen Arbeitsordner an und lädt bzw. kopiert das Quellvideo als source.mp4 hinein."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if re.match(r"https?://", source):
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(source, download=False)
        work = WORK / niche_name / f"{stamp}-{pipeline._slug(info.get('title') or 'video')}"
        work.mkdir(parents=True)
        opts = {
            "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
            "merge_output_format": "mp4",
            "outtmpl": str(work / "source.%(ext)s"),
            "quiet": True,
        }
        print(f"[{niche_name}] Lade {source} ...")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([source])
        found = next(work.glob("source.*"))
        if found.suffix != ".mp4":
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(found), "-c", "copy", str(work / "source.mp4")],
                           check=True)
            found.unlink()
        (work / "quelle.txt").write_text(source + "\n", encoding="utf-8")
    else:
        src = Path(source)
        work = WORK / niche_name / f"{stamp}-{pipeline._slug(src.stem)}"
        work.mkdir(parents=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-c", "copy", str(work / "source.mp4")],
                       check=True)
        (work / "quelle.txt").write_text(str(src) + "\n", encoding="utf-8")
    return work


# ---------------------------------------------------------------- Transkribieren

def _load_audio(path: Path):
    """Ton als 16-kHz-Mono-Array über FFmpeg (unabhängig von der PyAV-Version)."""
    import numpy as np

    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def transcribe(work: Path, language: str | None, model_size: str) -> dict:
    """Spracherkennung mit Wort-Zeitstempeln. Ergebnis: transcript.json und transkript.txt."""
    from faster_whisper import WhisperModel

    print(f"Transkribiere ({model_size}) ... das dauert auf der CPU etwa so lange wie das Video")
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, info = model.transcribe(_load_audio(work / "source.mp4"), language=language,
                                      word_timestamps=True, vad_filter=True)
    segs, words = [], []
    for seg in segments:
        segs.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        for w in seg.words or []:
            if w.word.strip():
                words.append({"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})
    data = {"language": info.language, "duration": info.duration, "segments": segs, "words": words}
    (work / "transcript.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"[{s['start']:8.2f} - {s['end']:8.2f}] {s['text']}" for s in segs]
    (work / "transkript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


# ---------------------------------------------------------------- Highlights auswählen

def select_with_claude(work: Path, niche: dict, count: int) -> list[dict]:
    import anthropic

    data = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    transcript = (work / "transkript.txt").read_text(encoding="utf-8")
    lo, hi = niche.get("clip_min", 20), niche.get("clip_max", 60)
    rules = niche.get("campaign_rules", "").strip()
    prompt = (
        f"Hier ist das Transkript eines Videos ({data['duration']:.0f} s) mit Zeitstempeln in Sekunden.\n\n"
        f"Wähle die {count} stärksten Momente für TikTok, Reels und Shorts aus.\n"
        f"- Jeder Clip ist {lo}-{hi} Sekunden lang, für sich verständlich und überschneidet sich nicht mit anderen.\n"
        "- Der erste Satz muss sofort fesseln (Pointe, Streit, Geständnis, überraschende Aussage, starke Meinung).\n"
        "- Start und Ende liegen an Satzgrenzen, nicht mitten im Wort.\n"
        "- Titel und Caption in der Sprache des Videos, Titel max. 80 Zeichen, keine Clickbait-Lügen.\n"
        "- Sortiere nach erwartetem Viral-Potenzial, stärkster Clip zuerst.\n"
        + (f"\nRegeln der Kampagne:\n{rules}\n" if rules else "")
        + f"\nTranskript:\n{transcript}"
    )
    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": AUSWAHL_SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"Auswahl durch Claude fehlgeschlagen: {response.stop_reason}")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)["clips"]


def select_heuristic(work: Path, niche: dict, count: int) -> list[dict]:
    """Notlösung ohne Claude: dichte, abgeschlossene Abschnitte mit Frage-/Ausrufezeichen bevorzugen."""
    data = json.loads((work / "transcript.json").read_text(encoding="utf-8"))
    segs = data["segments"]
    lo, hi = niche.get("clip_min", 20), niche.get("clip_max", 60)
    candidates = []
    for i in range(len(segs)):
        text, j = "", i
        while j < len(segs) and segs[j]["end"] - segs[i]["start"] <= hi:
            text += " " + segs[j]["text"]
            length = segs[j]["end"] - segs[i]["start"]
            if length >= lo and re.search(r"[.!?]$", segs[j]["text"]):
                words = len(text.split())
                score = words / length + 0.5 * text.count("!") + 0.5 * text.count("?")
                candidates.append((score, segs[i]["start"], segs[j]["end"], text.strip()))
            j += 1
    chosen = []
    for score, start, end, text in sorted(candidates, reverse=True):
        if all(end <= c["start"] or start >= c["end"] for c in chosen):
            title = re.split(r"(?<=[.!?])\s", text)[0][:80]
            chosen.append({"start": start, "end": end, "title": title, "description": title,
                           "hashtags": [], "reason": f"Heuristik (Score {score:.2f})"})
        if len(chosen) == count:
            break
    return chosen


def select(work: Path, niche_name: str, count: int) -> list[dict]:
    import os

    niche = pipeline.load_niches()[niche_name]
    if os.environ.get("ANTHROPIC_API_KEY"):
        print(f"[{niche_name}] Claude wählt die {count} besten Momente ...")
        clips = select_with_claude(work, niche, count)
    else:
        print(f"[{niche_name}] Kein ANTHROPIC_API_KEY: einfache Auswahl. Besser: in Claude Code den Skill "
              "clip-auswahl nutzen, dann `clips schneiden`.")
        clips = select_heuristic(work, niche, count)
    (work / "auswahl.json").write_text(json.dumps({"clips": clips}, ensure_ascii=False, indent=2), encoding="utf-8")
    return clips


# ---------------------------------------------------------------- Schneiden

def _snap(words: list[dict], start: float, end: float) -> tuple[float, float, list[dict]]:
    """Clipgrenzen an Wortgrenzen ausrichten und die Wörter des Clips (relativ zum Start) liefern."""
    inside = [w for w in words if w["start"] >= start - 0.3 and w["end"] <= end + 0.3]
    if not inside:
        return start, end, []
    s = max(inside[0]["start"] - 0.15, 0)
    e = inside[-1]["end"] + 0.35
    rel = [{"text": w["text"], "start": w["start"] - s, "end": w["end"] - s} for w in inside]
    return s, e, rel


def _gameplay_file(niche: dict) -> Path | None:
    folder = pipeline.ROOT / niche.get("gameplay_dir", "assets/gameplay")
    files = [p for p in folder.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")]
    return random.choice(files) if files else None


def render_clip(work: Path, clip: dict, words: list[dict], niche: dict, out_dir: Path) -> Path:
    W, H = render.W, render.H
    start, end, rel_words = _snap(words, clip["start"], clip["end"])
    duration = end - start
    out_dir.mkdir(parents=True)

    layout = niche.get("layout", "split")
    gameplay = _gameplay_file(niche) if layout == "split" else None
    src = _probe(work / "source.mp4")
    vertical = src["height"] > src["width"]

    subs = out_dir / "subtitles.ass"
    margin = H - H_HALF - 60 if gameplay else 620  # bei Split genau auf der Trennlinie
    render.write_subtitles(rel_words, subs, niche.get("subtitle_color", "#FFFFFF"), margin)

    cmd = ["ffmpeg", "-y", "-ss", f"{start:.2f}", "-t", f"{duration:.2f}", "-i", str((work / "source.mp4").resolve())]
    if gameplay:
        g_len = _probe(gameplay)["duration"]
        offset = random.uniform(0, max(g_len - duration - 1, 0))
        cmd += ["-stream_loop", "-1", "-ss", f"{offset:.2f}", "-i", str(gameplay.resolve())]
        graph = (
            f"[0:v]scale={W}:{H_HALF}:force_original_aspect_ratio=increase,crop={W}:{H_HALF}[top];"
            f"[1:v]scale={W}:{H_HALF}:force_original_aspect_ratio=increase,crop={W}:{H_HALF}[bot];"
            f"[top][bot]vstack=inputs=2,fps={render.FPS},subtitles={subs.name}[v]"
        )
    elif vertical:
        graph = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"fps={render.FPS},subtitles={subs.name}[v]")
    else:
        # Querformat ohne Gameplay: Video mittig, unscharfer Hintergrund aus demselben Bild
        graph = (
            f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5[bg];"
            f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={render.FPS},subtitles={subs.name}[v]"
        )
    out = out_dir / "video.mp4"
    cmd += [
        "-filter_complex", graph, "-map", "[v]", "-map", "0:a?", "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out.resolve()),
    ]
    subprocess.run(cmd, check=True, capture_output=True, cwd=out_dir)
    return out


def cut(work: Path, niche_name: str) -> list[Path]:
    niche = pipeline.load_niches()[niche_name]
    words = json.loads((work / "transcript.json").read_text(encoding="utf-8"))["words"]
    clips = json.loads((work / "auswahl.json").read_text(encoding="utf-8"))["clips"]
    source = (work / "quelle.txt").read_text(encoding="utf-8").strip()
    folders = []
    for i, clip in enumerate(clips, 1):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        folder = pipeline.OUTPUT / niche_name / f"{stamp}-{i:02d}-{pipeline._slug(clip['title'])}"
        print(f"[{niche_name}] Clip {i}/{len(clips)}: {clip['title']}")
        video = render_clip(work, clip, words, niche, folder)
        hashtags = list(dict.fromkeys(niche.get("hashtags", []) + clip.get("hashtags", [])))
        credit = niche.get("credit", "").strip()
        description = clip["description"] + (f"\n{credit}" if credit else "") + f"\n\n{' '.join(hashtags)}"
        pipeline._write_meta(folder, {
            "niche": niche_name,
            "status": "review",
            "title": clip["title"],
            "summary": clip.get("reason", ""),
            "description": description,
            "hashtags": hashtags,
            "video": video.name,
            "source": source,
            "clip_start": clip["start"],
            "clip_end": clip["end"],
        })
        folders.append(folder)
    return folders


def auto(source: str, niche_name: str, count: int) -> list[Path]:
    niche = pipeline.load_niches()[niche_name]
    work = prepare(source, niche_name)
    lang = niche.get("language") if len(niche.get("language", "")) == 2 else None
    transcribe(work, lang, niche.get("whisper_model", "small"))
    select(work, niche_name, count)
    return cut(work, niche_name)
