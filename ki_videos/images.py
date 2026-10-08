"""Erzeugt Bilder über fal.ai (Standard: FLUX)."""
import os
from pathlib import Path

import requests

# Modell kann über die Umgebungsvariable getauscht werden, z. B. fal-ai/flux-pro/v1.1
FAL_MODEL = os.environ.get("FAL_MODEL", "fal-ai/flux/dev")


def generate_image(prompt: str, out_path: Path) -> Path:
    api_key = os.environ["FAL_KEY"]
    resp = requests.post(
        f"https://fal.run/{FAL_MODEL}",
        headers={"Authorization": f"Key {api_key}"},
        json={
            "prompt": prompt,
            "image_size": {"width": 1080, "height": 1920},
            "num_images": 1,
        },
        timeout=300,
    )
    resp.raise_for_status()
    url = resp.json()["images"][0]["url"]

    img = requests.get(url, timeout=120)
    img.raise_for_status()
    out_path.write_bytes(img.content)
    return out_path
