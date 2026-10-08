# KI-Videos: automatische Pipeline für mehrere Nischen

Erzeugt Kurzvideos (9:16) komplett automatisch und lädt sie auf TikTok, Instagram, Facebook und YouTube hoch:

```
Claude (Skript, Szenen-Prompts, Titel, Hashtags, bei Serien: nächste Folge)
  ├─ mode: bilder → fal.ai FLUX (Bild pro Szene) → ElevenLabs (Stimme) → FFmpeg (Zoom + Untertitel)
  └─ mode: video  → fal.ai Veo 3 (8-Sek.-Clips mit Ton/Dialog) → FFmpeg (zusammenschneiden)
  → Ordner zur Prüfung
  → Upload-Post (alle Plattformen der jeweiligen Nische)
```

## Die drei Nischen (`config/niches.yaml`)

| Nische | Modus | Serie | Idee |
|---|---|---|---|
| `fruechte_drama` | video | ✅ | Obst-Soap mit festen Figuren (Erdbeere Emma, Banane Bernd …), jede Folge mit Cliffhanger |
| `ki_asmr` | video | – | Messer schneidet Glasfrüchte, Kristalle, Lava … ohne Sprache, funktioniert weltweit |
| `mythen_serie` | bilder | ✅ | Griechische, nordische und ägyptische Sagen als Fortsetzungsgeschichte (gemeinfrei, kein Urheberrecht-Problem) |

**Serien:** Die Pipeline merkt sich in `output/<nische>/history.json` eine Zusammenfassung jeder Folge. Claude schreibt die nächste Folge passend weiter. Ist eine Folge schlecht, löschst du sie mit `verwerfen`. Die nächste Folge wird dann an derselben Stelle neu geschrieben.

**Feste Figuren:** Unter `characters` beschreibst du das Aussehen jeder Figur auf Englisch. Diese Beschreibung kommt in jeden Clip-Prompt, damit die Figuren in allen Folgen gleich aussehen.

Die Schritt-für-Schritt-Anleitung und die Trends stehen in [ANLEITUNG.md](ANLEITUNG.md).

## Einrichtung

1. Python 3.10+ und FFmpeg installieren (`brew install ffmpeg`, `sudo apt install ffmpeg` oder ffmpeg.org).
2. Pakete installieren:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. API-Keys besorgen und in `.env` eintragen (Vorlage: `.env.example`):
   | Key | Woher | Wofür |
   |---|---|---|
   | `ANTHROPIC_API_KEY` | console.anthropic.com | Skripte |
   | `FAL_KEY` | fal.ai | Bilder |
   | `ELEVENLABS_API_KEY` | elevenlabs.io | Stimme |
   | `UPLOAD_POST_API_KEY` | upload-post.com | Upload |
4. In `config/niches.yaml` bei Nischen mit `mode: bilder` eine `voice_id` aus ElevenLabs eintragen (Voice Library, „ID kopieren“). Video-Nischen brauchen keine, weil der Ton aus dem Videomodell kommt.

## Mehrere Nischen und Accounts

**Ja, ein eigener Account-Satz pro Nische ist sinnvoll.** Der Algorithmus zeigt einem Account nur dann neue Zuschauer, wenn klar ist, worum es geht. Gemischte Themen auf einem Account bremsen das Wachstum.

Du brauchst **einen Account pro Plattform pro Nische**. Bei 3 Nischen und 5 Plattformen sind das bis zu 15. Der Aufwand ist kleiner, als es klingt:
- **YouTube:** ein Google-Konto, darunter mehrere Kanäle (Brand-Accounts)
- **Facebook:** ein privates Profil, darunter eine Seite pro Nische
- **Instagram:** bis zu 5 Accounts in einer App, jeder mit der passenden Facebook-Seite verknüpft
- **TikTok:** mehrere Accounts in einer App, jeder mit eigener E-Mail
- **Snapchat:** ein öffentliches Profil pro Nische

Am Anfang reichen **TikTok, Instagram und YouTube** (9 Accounts).

So richtest du es ein:
1. Pro Nische eigene Accounts auf den gewählten Plattformen anlegen.
2. Bei **Upload-Post** pro Nische ein **Profil** anlegen (z. B. `tierfakten`) und dort nur die Accounts dieser Nische verbinden.
3. In `config/niches.yaml` einen Block pro Nische eintragen. `upload_profile` muss genau wie das Upload-Post-Profil heißen.

Neue Nische = neuer Block in der YAML-Datei. Am Code musst du nichts ändern.

**Tipps:**
- Fang mit **2–3 Nischen** an und erweitere erst, wenn eine läuft. Jede Nische braucht Pflege (Kommentare, Auswertung).
- Accounts **nicht direkt** mit vielen Uploads pro Tag starten. In den ersten Tagen 1 Video pro Tag, dann steigern.
- Jede Nische braucht einen eigenen Stil (Stimme, Bildstil). Dann wirken die Accounts nicht wie Massenware.
- TikTok und Instagram erlauben mehrere Accounts pro Person. Verboten ist es aber, Accounts zu nutzen, um gegenseitig Reichweite zu pushen (Likes oder Kommentare zwischen den eigenen Accounts).

## Benutzung

```bash
python -m ki_videos nischen                                  # konfigurierte Nischen anzeigen
python -m ki_videos erstellen --nische tier_fakten           # ein Video erstellen
python -m ki_videos erstellen --nische tier_fakten --thema "Oktopus hat drei Herzen" --anzahl 3
python -m ki_videos erstellen --alle                         # ein Video pro Nische
python -m ki_videos offen                                    # was wartet auf Prüfung?
python -m ki_videos hochladen output/tier_fakten/2026...     # ein geprüftes Video hochladen
python -m ki_videos hochladen --alle-offenen                 # alle geprüften hochladen
python -m ki_videos verwerfen output/fruechte_drama/2026...  # schlechtes Video löschen
```

Jedes Video bekommt einen eigenen Ordner unter `output/<nische>/` mit `video.mp4`, `script.json`, den Bildern und `meta.json` (Titel, Beschreibung, Status). Bereits behandelte Themen merkt sich die Pipeline in `output/<nische>/history.json`, damit sich Themen nicht wiederholen.

**Prüfen vor dem Upload (empfohlen):** Standardmäßig wird nur erstellt. Sieh dir das Video kurz an, lösche den Ordner, wenn es nicht gut ist, und lade es sonst mit `hochladen` hoch. Mit `--hochladen` geht es ohne Prüfung direkt raus. Das ist erst sinnvoll, wenn die Qualität zuverlässig stimmt.

**Hintergrundmusik:** In der Nische `music: musik/meine_datei.mp3` eintragen (nur lizenzfreie Musik). Die Musik wird leise unter die Stimme gemischt.

## Vollautomatisch per Zeitplan

Ein Cronjob auf einem Server oder Raspberry Pi erstellt zum Beispiel jeden Morgen um 7 Uhr ein Video pro Nische:
```cron
0 7 * * * cd /pfad/zu/KI_Videos && .venv/bin/python -m ki_videos erstellen --alle >> log.txt 2>&1
```
Mittags prüfst du kurz und lädst hoch (`hochladen --alle-offenen`). Wenn du der Qualität vertraust, hängst du stattdessen `--hochladen` an.

## Kosten pro Video (grob)

| Dienst | ca. |
|---|---|
| Claude (Skript) | 1–3 Cent |
| **Bilder-Modus:** FLUX dev, 5–6 Bilder | 15–25 Cent |
| **Bilder-Modus:** ElevenLabs, ~40 Sek. Stimme | im Abo enthalten (Starter ~5 $/Monat reicht für ca. 30–60 Videos) |
| **Video-Modus:** Veo 3 fast, pro 8-Sek.-Clip | **ca. 1–3 $** (Früchte-Drama mit 4 Clips: ca. 4–12 $, ASMR mit 2 Clips: ca. 2–6 $) |
| Upload-Post | Abo ab ca. 8 $/Monat |

Der Video-Modus ist deutlich teurer. Günstigere Videomodelle auf fal.ai (z. B. Kling, Hailuo, Wan) trägst du pro Nische als `video_model` ein. Manche erzeugen aber keinen Ton.

Die Preise ändern sich oft, prüf sie auf den Seiten der Anbieter.

## Vor dem ersten echten Lauf prüfen

Der Videoschnitt ist lokal getestet. Die externen APIs konnten beim Bauen nicht live aufgerufen werden. Gleiche deshalb einmal ab:
- **Upload-Post** (`ki_videos/upload.py`): Endpunkt `api/upload`, Felder `user`, `platform[]`, `title`, `description`, `video`. Siehe docs.upload-post.com. Dort steht auch, ob es ein Feld für das **KI-Label** gibt. Sonst setzt du das Label einmalig in den App-Einstellungen bzw. pro Post.
- **fal.ai** (`ki_videos/images.py`): Feld `image_size` mit `width`/`height` für Bilder. Für Videos die Felder `aspect_ratio`, `duration`, `generate_audio` und die Antwort `video.url`. Diese Felder unterscheiden sich je nach Videomodell.
- **ElevenLabs** (`ki_videos/voice.py`): Endpunkt `with-timestamps`.

Am besten zuerst mit einem Test-Profil bei Upload-Post und privaten Test-Accounts ausprobieren.

## Snapchat

Upload-Post unterstützt Snapchat nicht. Optionen: ShortSync oder Dash Social (Spotlight-API), oder die fertige `video.mp4` manuell in Snapchat hochladen.

## Erweiterungsideen

- Figuren noch konsistenter machen: zuerst ein Referenzbild pro Figur erzeugen und Bild-zu-Video statt Text-zu-Video nutzen.
- Statistiken: Views pro Video abrufen und Claude bei neuen Themen die Bestseller mitgeben.
