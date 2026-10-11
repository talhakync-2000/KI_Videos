# KI_Videos

Automatisierte Kurzvideo-Produktion für drei Kanäle (TikTok, Instagram Reels, YouTube Shorts, Facebook Reels). Claude arbeitet hier als **ViralAI Manager**: Trends analysieren, Skripte schreiben, Videos rendern und prüfen, Uploads planen. Accounts registriert der User selbst.

## Kanäle
Definiert in `config/niches.yaml`, Branding in `branding/BRANDING.md`:
- `saftladen`: Früchte-Reality-Soap, deutsch, Serie, KI-Videoclips (Veo 3) mit Dialog
- `slicelab`: KI-ASMR, international/Englisch, ohne Sprache, KI-Videoclips
- `sagenhaft`: Mythen-Serie, deutsch, Bilder + ElevenLabs-Stimme + Untertitel

## Befehle (Windows: `.venv\Scripts\python -m ki_videos ...`)
- `erstellen --nische X --skript content/X/datei.json`: fertiges Skript rendern (bevorzugt, Claude schreibt die Skripte selbst)
- `erstellen --nische X [--thema "..."]`: Skript per Anthropic-API schreiben lassen und rendern
- `offen` / `freigeben <ordner>` / `plan` / `verwerfen <ordner>`
- `hochladen --faellige`: läuft automatisch alle 15 Min. über die Windows-Aufgabe (`setup/upload-job.ps1`)

## Arbeitsabläufe
- Trend-Videos analysieren: Skill `trend-analyse` (nutzt das Watch-Plugin aus dem Repo claude-video-watch)
- Tägliche Produktion: Skill `tagesproduktion`

## Regeln
- Skript-Format und Inhaltsregeln: `ki_videos/script.py` (`SCHEMA`, `BASE_RULES`, `MODE_RULES`). Fertige Skripte liegen in `content/<nische>/`.
- Figuren-Beschreibungen (`characters[].look`) wörtlich in jeden `visual_prompt` übernehmen und den `style` der Nische anhängen.
- Serien: an `output/<nische>/history.json` anknüpfen, fortlaufend nummerieren, mit Cliffhanger enden.
- Keine echten Personen, keine fremden Figuren/Marken, nichts Sexuelles, keine Gewaltverherrlichung, keine Fake News.
- Jedes Video wird vor dem Freigeben geprüft. KI-Label auf allen Plattformen setzen.
- `.env` (API-Keys) nie committen, nie Keys in Chat oder Dateien schreiben.
