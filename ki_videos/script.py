"""Erzeugt Skript, Bild-Prompts und Metadaten für ein Video mit Claude."""
import json

import anthropic

MODEL = "claude-opus-5-5"

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Kurzer Titel, max. 80 Zeichen"},
        "description": {"type": "string", "description": "1-2 Sätze Beschreibung"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "narration": {"type": "string"},
                    "image_prompt": {"type": "string"},
                },
                "required": ["narration", "image_prompt"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "description", "hashtags", "scenes"],
    "additionalProperties": False,
}

SYSTEM = """Du schreibst Skripte für virale Kurzvideos (TikTok, Reels, Shorts, Spotlight).

Regeln:
- Die erste Szene ist der Hook: ein Satz, der sofort neugierig macht. Keine Begrüßung.
- Gesamtlänge der Erzählung: 25-45 Sekunden gesprochen (ca. 70-120 Wörter).
- Kurze, gesprochene Sätze. Keine Emojis, keine Regieanweisungen im Erzähltext.
- Fakten müssen stimmen. Wenn etwas unsicher ist, lass es weg.
- Keine echten, lebenden Personen in den Bild-Prompts (keine Deepfakes).
- image_prompt immer auf Englisch, beschreibt ein einzelnes Hochformat-Bild (9:16) ohne Text im Bild.
- Die letzte Szene endet mit einer kurzen Frage oder einem Aufruf zum Folgen."""


def generate_script(niche: dict, theme: str | None, recent_titles: list[str]) -> dict:
    client = anthropic.Anthropic()

    parts = [
        f"Sprache der Erzählung: {niche['language']}",
        f"Nische: {niche['topic'].strip()}",
        f"Tonfall: {niche['tone']}",
        f"Anzahl Szenen: genau {niche.get('scenes', 5)}",
        f"Bildstil (an jeden image_prompt anhängen): {niche['image_style'].strip()}",
    ]
    if theme:
        parts.append(f"Thema oder Trend für dieses Video: {theme}")
    else:
        parts.append("Wähle selbst ein starkes Thema, das in diese Nische passt.")
    if recent_titles:
        parts.append(
            "Diese Themen gab es schon, wiederhole keines davon:\n- "
            + "\n- ".join(recent_titles[-50:])
        )

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={
            "effort": "medium",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        system=SYSTEM,
        messages=[{"role": "user", "content": "\n\n".join(parts)}],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude hat das Thema abgelehnt: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Antwort wurde abgeschnitten (max_tokens erreicht)")

    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)
