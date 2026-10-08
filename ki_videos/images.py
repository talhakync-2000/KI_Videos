"""Erzeugt Bilder und Videoclips über fal.ai.

Modelle lassen sich pro Nische (image_model / video_model) oder per Umgebungsvariable tauschen.
Feldnamen der Videomodelle unterscheiden sich je nach Modell: vor dem ersten Lauf auf fal.ai prüfen.
"""
import os
from pathlib import Path

import requests

DEFAULT_IMAGE_MODEL = os.environ.get("FAL_MODEL", "fal-ai/flux/dev")
DEFAULT_VIDEO_MODEL = os.environ.get("FAL_VIDEO_MODEL", "fal-ai/veo3/fast")


def _fal(model: str, payload: dict, timeout: int) -> dict:
    resp = requests.post(
        f"https://fal.run/{model}",
        headers={"Authorization": f"Key {os.environ['FAL_KEY']}"},
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def _download(url: str, out_path: Path) -> Path:
    resp = requests.get(url, timeout=300)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    return out_path


def generate_image(prompt: str, out_path: Path, model: str | None = None) -> Path:
    data = _fal(
        model or DEFAULT_IMAGE_MODEL,
        {"prompt": prompt, "image_size": {"width": 1080, "height": 1920}, "num_images": 1},
        timeout=300,
    )
    return _download(data["images"][0]["url"], out_path)


def generate_clip(prompt: str, out_path: Path, model: str | None = None) -> Path:
    """Text-zu-Video mit Ton (z. B. Veo 3). Dauert pro Clip oft 1-3 Minuten."""
    data = _fal(
        model or DEFAULT_VIDEO_MODEL,
        {"prompt": prompt, "aspect_ratio": "9:16", "duration": "8s", "generate_audio": True},
        timeout=900,
    )
    return _download(data["video"]["url"], out_path)
