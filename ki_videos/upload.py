"""Upload auf mehrere Plattformen über die Upload-Post-API (https://docs.upload-post.com/api/upload-video).

Snapchat wird von Upload-Post nicht unterstützt (separat, z. B. über ShortSync, oder manuell).
TikTok-Uploads gehen bei Upload-Post nur in einem bezahlten Tarif.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://api.upload-post.com/api/upload"
YOUTUBE_TITLE_MAX = 100
CAPTION_MAX = 2200  # TikTok und Instagram


def build_fields(meta: dict, niche: dict, platforms: list[str], publish_at: datetime | None) -> list[tuple[str, str]]:
    """Formularfelder für POST /api/upload.

    Upload-Post ignoriert `description` auf TikTok und Instagram, deshalb bekommen beide eine
    eigene Caption (Titel + Text + Hashtags). YouTube und Facebook nutzen title + description.
    """
    caption = f"{meta['title']}\n\n{meta['description']}"[:CAPTION_MAX]
    fields = [
        ("user", niche["upload_profile"]),
        ("title", meta["title"]),
        ("description", meta["description"]),
        ("tiktok_title", caption),
        ("instagram_title", caption),
        ("youtube_title", meta["title"][:YOUTUBE_TITLE_MAX]),
        # KI-Label auf TikTok, Instagram, YouTube (containsSyntheticMedia) und X; Facebook extra
        ("is_ai_generated", "true"),
        ("facebook_is_ai_generated", "true"),
        ("selfDeclaredMadeForKids", "false"),
        ("categoryId", str(niche.get("youtube_category", "24"))),
    ]
    fields += [("platform[]", p) for p in platforms]
    fields += [("tags[]", tag.lstrip("#")) for tag in meta.get("hashtags", [])]
    if len(niche.get("language", "")) == 2:
        fields.append(("defaultLanguage", niche["language"]))
    if niche.get("youtube_playlist_id"):
        fields.append(("youtube_playlist_id", niche["youtube_playlist_id"]))
    if publish_at:
        utc = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        fields.append(("scheduled_date", utc))
    return fields


def upload_video(video: Path, fields: list[tuple[str, str]], idempotency_key: str) -> dict:
    with open(video, "rb") as f:
        resp = requests.post(
            API_URL,
            headers={
                "Authorization": f"Apikey {os.environ['UPLOAD_POST_API_KEY']}",
                # Wird derselbe Upload wiederholt (z. B. nach Timeout), gibt es keinen Doppel-Post
                "Idempotency-Key": idempotency_key,
            },
            data=fields,
            files={"video": (video.name, f, "video/mp4")},
            timeout=900,
        )
    try:
        data = resp.json()
    except ValueError:
        data = {}
    if resp.status_code >= 400 or not data.get("success", False):
        raise RuntimeError(f"Upload-Post {resp.status_code}: {data.get('message') or resp.text[:300]}")
    return data


def failed_platforms(result: dict) -> list[str]:
    """Plattformen, die in einer synchronen Antwort einzeln fehlgeschlagen sind."""
    return [p for p, r in (result.get("results") or {}).items() if not r.get("success")]
