"""Erzeugt Skript, Szenen-Prompts und Metadaten für ein Video mit Claude."""
import json

import anthropic

MODEL = "claude-opus-5-5"

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Kurzer Titel, max. 80 Zeichen"},
        "description": {"type": "string", "description": "1-2 Sätze Beschreibung"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "episode_summary": {
            "type": "string",
            "description": "2-3 Sätze: was in diesem Video passiert (für die Fortsetzung)",
        },
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "narration": {"type": "string"},
                    "visual_prompt": {"type": "string"},
                },
                "required": ["narration", "visual_prompt"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "description", "hashtags", "episode_summary", "scenes"],
    "additionalProperties": False,
}

BASE_RULES = """Du schreibst Skripte für virale Kurzvideos (TikTok, Reels, Shorts, Spotlight).

Allgemeine Regeln:
- Die ersten 1-2 Sekunden müssen sofort fesseln. Keine Begrüßung, kein Intro.
- Keine echten, lebenden Personen und keine geschützten Figuren aus Filmen, Serien oder Marken.
- Nichts Sexuelles, keine Gewaltverherrlichung, nichts gegen Gruppen von Menschen.
- visual_prompt immer auf Englisch, Hochformat 9:16, kein Text oder Schrift im Bild."""

MODE_RULES = {
    "bilder": """Format: Standbilder mit Erzählstimme.
- narration: gesprochener Erzähltext der Szene. Gesamt 25-45 Sekunden (ca. 70-120 Wörter), kurze Sätze, keine Emojis.
- visual_prompt: beschreibt ein einzelnes Standbild.
- Fakten müssen stimmen. Wenn etwas unsicher ist, lass es weg.
- Die letzte Szene endet mit einer Frage oder einem Aufruf zum Folgen.""",
    "video": """Format: KI-Videoclips (je ca. 8 Sekunden) mit Ton, den das Videomodell selbst erzeugt.
- narration: leer lassen ("").
- visual_prompt: beschreibt einen 8-Sekunden-Clip vollständig: Figuren, Handlung, Kamera, Licht,
  und unter "Audio:" die Geräusche und, falls jemand spricht, die exakten Dialogzeilen in der
  Zielsprache mit Angabe, wer sie sagt (maximal 1-2 kurze Sätze pro Clip).
- Jeder Clip ist für sich verständlich, weil die Clips hart hintereinander geschnitten werden.
- Wenn Figuren vorgegeben sind, übernimm ihre Aussehen-Beschreibung in JEDEN visual_prompt wörtlich,
  damit sie in allen Clips gleich aussehen.""",
}


def generate_script(niche: dict, theme: str | None, history: list[dict]) -> dict:
    client = anthropic.Anthropic()
    mode = niche.get("mode", "bilder")

    parts = [
        f"Sprache (Erzählung/Dialoge): {niche['language']}",
        f"Nische: {niche['topic'].strip()}",
        f"Tonfall: {niche['tone']}",
        f"Anzahl Szenen: genau {niche.get('scenes', 5)}",
        f"Visueller Stil (an jeden visual_prompt anhängen): {niche['style'].strip()}",
    ]
    if niche.get("characters"):
        chars = "\n".join(f"- {c['name']}: {c['look'].strip()}" for c in niche["characters"])
        parts.append(f"Feste Figuren dieser Serie:\n{chars}")
    if theme:
        parts.append(f"Thema oder Trend für dieses Video: {theme}")

    if niche.get("series") and history:
        recent = history[-8:]
        story = "\n".join(f"Folge {len(history) - len(recent) + i + 1}: {h['summary']}" for i, h in enumerate(recent))
        parts.append(
            f"Bisherige Folgen:\n{story}\n\nSchreibe Folge {len(history) + 1}. Knüpfe an die letzte Folge an "
            "und ende mit einem Cliffhanger. Beginne den Titel mit 'Folge "
            f"{len(history) + 1}:'."
        )
    elif niche.get("series"):
        parts.append("Das ist Folge 1. Stelle die Figuren kurz vor und ende mit einem Cliffhanger. "
                     "Beginne den Titel mit 'Folge 1:'.")
    elif history:
        parts.append("Diese Themen gab es schon, wiederhole keines davon:\n- "
                     + "\n- ".join(h["title"] for h in history[-50:]))

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={
            "effort": "medium",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        system=f"{BASE_RULES}\n\n{MODE_RULES[mode]}",
        messages=[{"role": "user", "content": "\n\n".join(parts)}],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude hat das Thema abgelehnt: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Antwort wurde abgeschnitten (max_tokens erreicht)")

    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)
