# KI-Videos: automatische Pipeline für drei Kanäle

Erzeugt Kurzvideos (9:16), plant sie auf die besten Posting-Zeiten und lädt sie automatisch auf TikTok, Instagram, Facebook und YouTube hoch.

```
Skript (Claude Code schreibt nach content/  ODER  Anthropic-API)
  ├─ mode: bilder → fal.ai FLUX (Bild pro Szene) → ElevenLabs (Stimme) → FFmpeg (Zoom + Untertitel)
  └─ mode: video  → fal.ai Veo 3 (8-Sek.-Clips mit Ton/Dialog) → FFmpeg (zusammenschneiden)
  → Prüfung (du oder Claude mit dem Watch-Plugin)
  → freigeben: nächster Posting-Slot der Nische
  → Windows-Aufgabe lädt zur geplanten Zeit über Upload-Post hoch
```

## Die drei Kanäle

| Kanal | Nische | Modus | Serie | Posting |
|---|---|---|---|---|
| **Saftladen** 🍓 (`saftladen`) | Früchte-Reality-Soap, deutsch | video | ✅ | täglich 19:00 |
| **SliceLab** 🔪 (`slicelab`) | KI-ASMR, international | video | – | 19:00 + 01:00 |
| **Sagenhaft** ⚡ (`sagenhaft`) | Mythen als Serie, deutsch | bilder | ✅ | täglich 18:00 |

- **Branding zum Kopieren** (Namen, Handles, Bios, Profilbild- und Banner-Prompts, Checkliste): [branding/BRANDING.md](branding/BRANDING.md)
- **Start-Content:** 3 Saftladen-Folgen, 5 SliceLab-Videos, 3 Sagenhaft-Folgen als fertige Skripte in `content/`
- **Allgemeine Anleitung und Trends:** [ANLEITUNG.md](ANLEITUNG.md)

## Einrichtung (Windows)

1. Repo herunterladen, im Ordner PowerShell öffnen:
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup\install.ps1
   ```
   Das Skript installiert Python und FFmpeg (per winget), legt `.venv` an und installiert die Pakete. Wenn es neue Programme installiert hat, Terminal neu öffnen und das Skript nochmal starten.
2. API-Keys in `.env` eintragen (`notepad .env`):
   | Key | Woher | Wofür | Nötig? |
   |---|---|---|---|
   | `FAL_KEY` | fal.ai | Bilder und Videoclips | ja |
   | `ELEVENLABS_API_KEY` | elevenlabs.io | Stimme (Sagenhaft) | ja |
   | `UPLOAD_POST_API_KEY` | upload-post.com | Upload | ja |
   | `ANTHROPIC_API_KEY` | console.anthropic.com | Skripte ohne Claude Code | nein, wenn Claude Code die Skripte schreibt |
3. In `config/niches.yaml` bei `sagenhaft` eine `voice_id` aus ElevenLabs eintragen (Voice Library, tiefe Erzählerstimme).
4. Automatische Uploads einschalten:
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup\upload-job.ps1
   ```
5. Für Trend-Analyse und Qualitätskontrolle: das Watch-Plugin aus dem Repo `claude-video-watch` einrichten (dort `install-deps.ps1`).

Auf Mac/Linux: Python 3.10+ und FFmpeg installieren, `python -m venv .venv`, `pip install -r requirements.txt`, statt der Windows-Aufgabe ein Cronjob `*/15 * * * * cd /pfad && .venv/bin/python -m ki_videos hochladen --faellige`.

## Benutzung

```powershell
$py = ".venv\Scripts\python"
& $py -m ki_videos nischen                                   # Kanäle, Modi, Posting-Slots
& $py -m ki_videos erstellen --nische saftladen --skript content\saftladen\folge-01.json content\saftladen\folge-02.json
& $py -m ki_videos erstellen --nische sagenhaft --thema "Thor und der Riese"   # Skript per Anthropic-API
& $py -m ki_videos offen                                     # wartet auf Prüfung
& $py -m ki_videos freigeben --alle-offenen                  # auf die nächsten freien Slots legen
& $py -m ki_videos plan                                      # was geht wann online?
& $py -m ki_videos verwerfen output\saftladen\2026...        # schlechtes Video löschen
& $py -m ki_videos hochladen output\slicelab\2026...         # sofort hochladen, ohne Slot
```

Jedes Video bekommt einen Ordner unter `output/<nische>/` mit `video.mp4`, `script.json` und `meta.json` (Upload-Paket: Titel, Beschreibung, Hashtags, Status, geplante Zeit). Der Status läuft `review` → `scheduled` → `uploaded`.

**Serien:** `output/<nische>/history.json` speichert eine Zusammenfassung jeder Folge, die nächste Folge knüpft daran an. Eine verworfene Folge wird aus der Historie gelöscht. Serien-Folgen immer in der richtigen Reihenfolge rendern und freigeben.

**Feste Figuren:** Unter `characters` steht das Aussehen jeder Figur auf Englisch. Es kommt wörtlich in jeden Prompt, damit die Figuren gleich aussehen.

**Upload-Zeiten:** `posting_times` pro Kanal in `config/niches.yaml`. Ist der PC zur Posting-Zeit aus, wird das Video beim nächsten Lauf der Aufgabe nachgeholt.

## Mit Claude Code arbeiten (ViralAI Manager)

Öffne Claude Code im Ordner `KI_Videos`. Die `CLAUDE.md` erklärt Claude das Projekt, dazu gibt es zwei Skills:
- **`/trend-analyse <Link>`**: Claude sieht sich ein virales Video mit dem Watch-Plugin an, erklärt, warum es viral geht, speichert die Analyse in `trends/` und schreibt passende neue Skripte nach `content/`.
- **`/tagesproduktion`**: Claude füllt die nächsten 3 Tage pro Kanal auf. Es schreibt Skripte, rendert, prüft jedes Video mit dem Watch-Plugin und gibt die guten frei.

So brauchst du keinen Anthropic-API-Key: Claude Code schreibt die Skripte selbst.

## Kosten pro Video (grob)

| Kanal | ca. pro Video |
|---|---|
| Saftladen (4 Veo-Clips) | 4–12 $ |
| SliceLab (2 Veo-Clips) | 2–6 $ |
| Sagenhaft (6 Bilder + Stimme) | unter 0,50 $ + ElevenLabs-Abo (~5 $/Monat) |
| Upload-Post | Abo ab ca. 8 $/Monat |

Video-Clips sind der große Kostenblock. Günstigere Videomodelle auf fal.ai (z. B. Kling, Hailuo, Wan) trägst du pro Kanal als `video_model` ein. Manche erzeugen aber keinen Ton. Die Preise ändern sich oft, prüf sie bei den Anbietern.

## Vor dem ersten echten Lauf prüfen

Der Videoschnitt, die Planung und der Upload-Ablauf sind mit Testdaten geprüft. Die externen APIs konnten beim Bauen nicht live aufgerufen werden. Gleiche deshalb einmal ab:
- **Upload-Post** (`ki_videos/upload.py`): Endpunkt `api/upload`, Felder `user`, `platform[]`, `title`, `description`, `video`. Siehe docs.upload-post.com. Dort steht auch, ob es ein Feld für das KI-Label gibt.
- **fal.ai** (`ki_videos/images.py`): Bilder mit `image_size` (`width`/`height`). Videos mit `aspect_ratio`, `duration`, `generate_audio`, Antwort `video.url`. Das unterscheidet sich je nach Videomodell.
- **ElevenLabs** (`ki_videos/voice.py`): Endpunkt `with-timestamps`.

Am besten zuerst ein einzelnes SliceLab-Video rendern (günstig, ohne Sprache) und mit einem Test-Profil bei Upload-Post hochladen.

## Snapchat

Upload-Post unterstützt Snapchat nicht. Optionen: ShortSync oder Dash Social (Spotlight-API), oder die fertige `video.mp4` manuell hochladen.
