"""Lädt ein Video über die Upload-Post-API auf mehrere Plattformen hoch.

Nutzung:
    export UPLOAD_POST_API_KEY=...
    python scripts/upload.py video.mp4 "Titel #hashtag" --user mein_profil \
        --platforms tiktok instagram facebook youtube

Endpunkt und Felder vor dem ersten Einsatz mit https://docs.upload-post.com/ abgleichen.
Snapchat wird von Upload-Post nicht unterstützt (separat, z. B. über ShortSync).
"""
import argparse
import os
import sys

import requests

API_URL = "https://api.upload-post.com/api/upload"


def upload(video_path, title, user, platforms):
    api_key = os.environ.get("UPLOAD_POST_API_KEY")
    if not api_key:
        sys.exit("UPLOAD_POST_API_KEY ist nicht gesetzt")

    data = [("user", user), ("title", title)]
    data += [("platform[]", p) for p in platforms]

    with open(video_path, "rb") as f:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Apikey {api_key}"},
            data=data,
            files={"video": f},
            timeout=600,
        )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("title")
    parser.add_argument("--user", required=True, help="Profilname bei Upload-Post")
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["tiktok", "instagram", "facebook", "youtube"],
    )
    args = parser.parse_args()
    print(upload(args.video, args.title, args.user, args.platforms))
