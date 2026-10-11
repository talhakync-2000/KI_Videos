# KI-Videos: automatische Pipeline für mehrere Kanäle

Erzeugt Kurzvideos (9:16), plant sie auf die besten Posting-Zeiten und lädt sie automatisch auf TikTok, Instagram, Facebook und YouTube hoch.

```
Skript (Claude Code schreibt nach content/  ODER  Anthropic-API)
  ├─ mode: bilder → fal.ai FLUX (Bild pro Szene) → ElevenLabs (Stimme) → FFmpeg (Zoom + Untertitel)
  └─ mode: video  → fal.ai Veo 3 (8-Sek.-Clips mit Ton/Dialog) → FFmpeg (zusammenschneiden)
  → Prüfung (du oder Claude mit dem Watch-Plugin)
  → freigeben: nächster Posting-Slot der Nische
  → Upload-Post bekommt das Video sofort und veröffentlicht es selbst zur Posting-Zeit
    (Fallback: Windows-Aufgabe lädt zur Posting-Zeit hoch, falls der sofortige Upload scheitert)
```

## Die Kanäle

Priorität laut [Marktanalyse](trends/2026-10-11-marktanalyse.md):

| # | Kanal | Nische | Modus | Serie | Posting | Status |
|---|---|---|---|---|---|---|
| 1 | **Kapitalverbrechen** 💰 (`kapitalverbrechen`) | Wirtschafts-Krimis, deutsch | bilder | Akten | täglich 20:00 | **Start** |
| 2 | **Sagenhaft** ⚡ (`sagenhaft`) | Mythen als Serie, deutsch | bilder | ✅ | täglich 18:00 | **Start** |
| 3 | **Saftladen** 🍓 (`saftladen`) | Früchte-Reality-Soap, deutsch | video | ✅ | täglich 19:00 | später |
| – | **SliceLab** 🔪 (`slicelab`) | KI-ASMR, international | video | – | 19:00 + 01:00 | pausiert |

Videos im Bilder-Modus sind 60–80 Sekunden lang, weil TikTok Creator Rewards nur Videos ab 60 Sekunden bezahlt.

- **Branding zum Kopieren** (Namen, Handles, Bios, Profilbild- und Banner-Prompts, Checkliste): [branding/BRANDING.md](branding/BRANDING.md)
- **Start-Content:** 3 Kapitalverbrechen-Akten, 3 Sagenhaft-Folgen, 3 Saftladen-Folgen, 5 SliceLab-Videos als fertige Skripte in `content/`
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
3. In `config/niches.yaml` bei `kapitalverbrechen` und `sagenhaft` je eine `voice_id` aus ElevenLabs eintragen (Voice Library). Kapitalverbrechen: ruhige, tiefe Podcast-Stimme. Sagenhaft: epischer Erzähler. Nimm zwei verschiedene Stimmen, damit die Kanäle unterscheidbar bleiben.
4. Fallback-Upload einschalten (lädt Videos nach, deren sofortiger Upload gescheitert ist):
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

**Upload-Zeiten:** `posting_times` pro Kanal in `config/niches.yaml`. `freigeben` schickt das Video sofort an Upload-Post, mit der Posting-Zeit als `scheduled_date`. Der PC muss zur Posting-Zeit also **nicht** laufen. Scheitert der sofortige Upload, bleibt das Video lokal geplant und die Windows-Aufgabe lädt es zur Posting-Zeit hoch. Mit `freigeben --lokal` geht es immer über die Windows-Aufgabe.

**Was beim Upload automatisch gesetzt wird:**
- eigene Caption für TikTok und Instagram (Titel, Text, Hashtags)
- YouTube-Titel (max. 100 Zeichen) mit Tags und Kategorie
- KI-Label auf allen Plattformen
- „Nicht für Kinder“ auf YouTube
- Schutz vor Doppel-Posts

Schlägt eine einzelne Plattform fehl, zeigt `plan` das an, und `hochladen <ordner>` versucht nur diese Plattform erneut.

## Mit Claude Code arbeiten (ViralAI Manager)

Öffne Claude Code im Ordner `KI_Videos`. Die `CLAUDE.md` erklärt Claude das Projekt, dazu gibt es zwei Skills:
- **`/trend-analyse <Link>`**: Claude sieht sich ein virales Video mit dem Watch-Plugin an, erklärt, warum es viral geht, speichert die Analyse in `trends/` und schreibt passende neue Skripte nach `content/`.
- **`/tagesproduktion`**: Claude füllt die nächsten 3 Tage pro Kanal auf. Es schreibt Skripte, rendert, prüft jedes Video mit dem Watch-Plugin und gibt die guten frei.

So brauchst du keinen Anthropic-API-Key: Claude Code schreibt die Skripte selbst.

## Kosten pro Video (grob)

| Kanal | ca. pro Video |
|---|---|
| Kapitalverbrechen (8 Bilder + Stimme) | unter 0,50 $ |
| Sagenhaft (7 Bilder + Stimme) | unter 0,50 $ |
| ElevenLabs für beide | Abo ca. 5–22 $/Monat, je nach Menge |
| Saftladen (4 Veo-Clips, 32 s) | 4–12 $ |
| SliceLab (2 Veo-Clips) | 2–6 $ |
| Upload-Post | Abo ab ca. 8 $/Monat |

Video-Clips sind der große Kostenblock. Günstigere Videomodelle auf fal.ai (z. B. Kling, Hailuo, Wan) trägst du pro Kanal als `video_model` ein. Manche erzeugen aber keinen Ton. Die Preise ändern sich oft, prüf sie bei den Anbietern.

## Vor dem ersten echten Lauf

Die API-Aufrufe sind gegen die offiziellen Dokumentationen geprüft (Stand 11.10.2026): Upload-Post `POST /api/upload`, fal.ai `veo3/fast` und `flux/dev`, ElevenLabs `with-timestamps`. Videoschnitt, Planung und Upload-Ablauf sind mit Testdaten geprüft. Ein echter Lauf mit deinen Keys steht noch aus.

- **Upload-Post-Tarif:** TikTok-Uploads gehen **nur in einem bezahlten Tarif**. TikTok erlaubt höchstens 15 Posts pro Tag und Account.
- **Facebook:** Pro Upload-Post-Profil genau **eine** Facebook-Seite verbinden. Dann wird sie automatisch genutzt, sonst verlangt die API eine `facebook_page_id`.
- **TikTok-Konto:** Upload-Post veröffentlicht mit der Standard-Sichtbarkeit des Kontos. Das TikTok-Konto muss also öffentlich sein.
- **Veo-Auflösung:** Standard ist 720p (günstiger). Die Pipeline skaliert auf 1080×1920 hoch.

Am besten zuerst eine Kapitalverbrechen-Akte rendern (günstig) und mit `hochladen <ordner>` sofort auf einen Test-Account hochladen.

## Snapchat

Upload-Post unterstützt Snapchat nicht. Optionen: ShortSync oder Dash Social (Spotlight-API), oder die fertige `video.mp4` manuell hochladen.
