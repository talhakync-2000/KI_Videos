"""Upload auf mehrere Plattformen über die Upload-Post-API.

Endpunkt und Feldnamen vor dem ersten Einsatz mit https://docs.upload-post.com/ abgleichen.
Snapchat wird von Upload-Post nicht unterstützt (separat, z. B. über ShortSync, oder manuell).
"""
import os
from pathlib import Path

import requests

API_URL = "https://api.upload-post.com/api/upload"


def upload_video(video: Path, title: str, description: str, profile: str, platforms: list[str]) -> dict:
    data = [("user", profile), ("title", title), ("description", description)]
    data += [("platform[]", p) for p in platforms]

    with open(video, "rb") as f:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Apikey {os.environ['UPLOAD_POST_API_KEY']}"},
            data=data,
            files={"video": f},
            timeout=900,
        )
    resp.raise_for_status()
    return resp.json()
