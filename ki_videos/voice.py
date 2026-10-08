"""Erzeugt das Voiceover über ElevenLabs inklusive Zeitstempeln pro Zeichen."""
import base64
import os
from pathlib import Path

import requests

ELEVEN_MODEL = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")


def generate_voice(text: str, voice_id: str, out_path: Path) -> dict:
    """Speichert die MP3 und gibt das Alignment (Zeichen + Start/Ende in Sekunden) zurück."""
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        json={"text": text, "model_id": ELEVEN_MODEL},
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    out_path.write_bytes(base64.b64decode(data["audio_base64"]))
    return data["alignment"]


def words_from_alignment(alignment: dict) -> list[dict]:
    """Fasst die Zeichen-Zeitstempel zu Wörtern zusammen: [{text, start, end, char_start}]."""
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    words, current = [], None
    for i, ch in enumerate(chars):
        if ch.isspace():
            if current:
                words.append(current)
                current = None
            continue
        if current is None:
            current = {"text": "", "start": starts[i], "end": ends[i], "char_start": i}
        current["text"] += ch
        current["end"] = ends[i]
    if current:
        words.append(current)
    return words
