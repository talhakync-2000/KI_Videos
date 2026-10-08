"""Baut aus Bildern, Voiceover und Wort-Zeitstempeln ein 9:16-Video mit FFmpeg."""
import subprocess
from pathlib import Path

W, H, FPS = 1080, 1920, 30
WORDS_PER_SUBTITLE = 3


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def scene_durations(scene_texts: list[str], alignment: dict, total: float) -> list[float]:
    """Szenenlänge = Zeit, in der der Erzähltext dieser Szene gesprochen wird."""
    starts = alignment["character_start_times_seconds"]
    offsets, pos = [], 0
    for text in scene_texts:
        offsets.append(min(pos, len(starts) - 1))
        pos += len(text) + 1  # +1 für das Leerzeichen beim Zusammenfügen
    times = [0.0] + [starts[o] for o in offsets[1:]] + [total]
    return [max(times[i + 1] - times[i], 0.5) for i in range(len(scene_texts))]


def _ken_burns_clip(image: Path, duration: float, out: Path, zoom_in: bool) -> None:
    frames = max(int(duration * FPS), 1)
    zoom = f"1+0.15*on/{frames}" if zoom_in else f"1.15-0.15*on/{frames}"
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"scale={W * 2}:{H * 2},"
        f"zoompan=z='{zoom}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={W}x{H}:fps={FPS}"
    )
    _run([
        "ffmpeg", "-y", "-i", str(image), "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out),
    ])


def _ass_time(t: float) -> str:
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_subtitles(words: list[dict], out: Path) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,620,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i in range(0, len(words), WORDS_PER_SUBTITLE):
        group = words[i:i + WORDS_PER_SUBTITLE]
        text = " ".join(w["text"] for w in group).upper()
        lines.append(
            f"Dialogue: 0,{_ass_time(group[0]['start'])},{_ass_time(group[-1]['end'])},"
            f"Default,,0,0,0,,{text}"
        )
    out.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def render_video(
    images: list[Path],
    durations: list[float],
    voice: Path,
    subtitles: Path,
    out: Path,
    music: Path | None = None,
) -> Path:
    work = out.parent / "_clips"
    work.mkdir(exist_ok=True)

    clips = []
    for i, (img, dur) in enumerate(zip(images, durations)):
        clip = work / f"clip_{i:02d}.mp4"
        _ken_burns_clip(img, dur, clip, zoom_in=(i % 2 == 0))
        clips.append(clip)

    concat_list = work / "clips.txt"
    concat_list.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-i", str(voice)]
    sub_filter = f"subtitles='{subtitles.resolve()}'"
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        cmd += [
            "-filter_complex",
            f"[0:v]{sub_filter}[v];[2:a]volume=0.12[m];"
            "[1:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
            "-map", "[v]", "-map", "[a]",
        ]
    else:
        cmd += ["-vf", sub_filter, "-map", "0:v", "-map", "1:a"]
    cmd += [
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out),
    ]
    _run(cmd)
    return out
