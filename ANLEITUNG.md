# KI-Videos: Anleitung von der Idee bis zum Upload

Stand: Oktober 2026

## 1. Aktuelle TikTok-Trends (Oktober 2026)

| Trend | Was es ist | Passt zu KI? |
|---|---|---|
| **Rumpelstiltskin „Tip Toein' In My Jordans“** | Ein Clip aus einem 80er-Fantasyfilm, in dem die Figur gegen Promis oder andere Figuren getauscht wird | ✅ Sehr gut: mit Viggle AI oder ähnlichen Tools (Figur + Bewegungsvorlage) |
| **„Answer in One Word“** | Man stellt ChatGPT persönliche Fragen, die es mit einem Wort beantworten muss, und filmt den Bildschirm | ✅ Gut: unter 20 Sekunden halten, schnell posten (der Trend ist nach 24–48 Std. vorbei) |
| **„Two Fishes“** | Ein Sound von einem Love-Island-USA-Kandidaten, mit dem man Streits „gewinnt“ | ⚠️ Nur mit KI-Avatar oder Animation |
| **KI-„Brainrot“ (Tierhybride mit italienischer TTS-Stimme)** | Gibt es seit 2025, das Format läuft aber noch | ✅ Leicht zu automatisieren, aber der Markt ist voll |

**Trends selbst prüfen (am besten täglich, ca. 10 Minuten):**
- TikTok Creative Center: creativecenter.tiktok.com, dort *Trends → Hashtags / Songs / Creators*, Region DE oder US
- Die „Für dich“-Seite mit einem eigenen Recherche-Account, der nur Inhalte aus deiner Nische ansieht
- Google Trends und die YouTube-Shorts-Trends als Gegencheck

> Hinweis: Trend-Blogs sind oft veraltet. Prüfe jeden Trend im Creative Center, bevor du ihn produzierst.

---

## 2. Schritt für Schritt

### Phase A: Einrichtung (einmalig, ca. 1–2 Tage)
1. **Nische wählen.** Ein Thema mit wiederkehrendem Format, z. B. KI-Geschichte, Fakten, Fake-Trailer, Tier-Edits, Motivation oder Comedy-Avatare. Ein klares Format wächst schneller als bunt gemischte Inhalte.
2. **Accounts anlegen:** TikTok, Instagram (als **Business- oder Creator-Account**, verknüpft mit einer **Facebook-Seite**), YouTube-Kanal und Snapchat Public Profile. Überall denselben Namen und dasselbe Profilbild verwenden.
3. **Tool-Stack festlegen:**
   - Skript und Ideen: ChatGPT oder Claude
   - Bilder: Midjourney, Flux, Ideogram
   - Video: Kling, Runway, Veo, Sora, Hailuo, Pika; für Trend-Edits mit Bewegung **Viggle AI**
   - Stimme: ElevenLabs
   - Musik: Suno oder Udio (Lizenz prüfen); bei Trend-Sounds **direkt in der TikTok-App** den Sound hinzufügen
   - Schnitt und Untertitel: CapCut, Descript oder automatisch per FFmpeg und Whisper
   - Upload: siehe Abschnitt 4
4. **Vorlagen bauen:** Intro-Hook (erste 1–2 Sekunden), Untertitel-Stil, Endcard und Hashtag-Sets pro Plattform.

### Phase B: Produktion (pro Video)
5. **Trend auswählen** (Abschnitt 1) und an deine Nische anpassen.
6. **Hook und Skript schreiben** (15–45 Sekunden). Die erste Sekunde muss neugierig machen.
7. **Bilder und Clips generieren**, ein Clip pro Szene (3–6 Szenen).
8. **Voiceover erzeugen** (ElevenLabs).
9. **Schneiden:** 9:16, 1080×1920, 30 fps, MP4 (H.264). Schnelle Schnitte (alle 1–3 Sekunden) und große Untertitel.
10. **Qualität prüfen:** Gibt es KI-Fehler (Hände, Text im Bild)? Ist alles verständlich ohne Ton?
11. **Metadaten erstellen:** Titel, Beschreibung, 3–5 Hashtags pro Plattform und ein Thumbnail für YouTube.

### Phase C: Veröffentlichen und auswerten
12. **Uploaden** (manuell oder automatisch, siehe Abschnitt 4), **mit KI-Label** (siehe Abschnitt 5).
13. **In der ersten Stunde** auf Kommentare antworten.
14. **Wöchentlich auswerten:** Watchtime und Retention ansehen. Was funktioniert, wird wiederholt; was floppt, wird gestrichen.
15. **Rhythmus:** Am Anfang 1–3 Videos pro Tag. Konstanz ist wichtiger als Perfektion.

---

## 3. Was du automatisieren kannst

| Schritt | Automatisierbar? | Womit |
|---|---|---|
| Trend-Recherche | 🟡 Teilweise | Creative Center ansehen; Scraper sind riskant (Verstoß gegen die AGB). Lieber manuell, ca. 10 Min. am Tag |
| Ideen, Skripte, Hooks | 🟢 Ja | LLM-API (Claude oder OpenAI) mit festem Prompt |
| Bilder und Video | 🟢 Ja | APIs von Runway, Kling, Veo, Replicate oder fal.ai |
| Voiceover | 🟢 Ja | ElevenLabs-API |
| Untertitel | 🟢 Ja | Whisper und FFmpeg |
| Schnitt und Zusammenbau | 🟢 Ja | FFmpeg, MoviePy, Remotion, Creatomate oder Shotstack |
| Titel und Hashtags | 🟢 Ja | LLM-API |
| **Upload auf alle Plattformen** | 🟢 Ja | Siehe Abschnitt 4 |
| Planung (Posting-Zeiten) | 🟢 Ja | Scheduler-Tool, Cronjob oder n8n |
| Trend-Sounds auf TikTok | 🔴 Nein | Lizenzierte Trend-Sounds lassen sich nur in der App hinzufügen |
| Qualitätskontrolle | 🔴 Nein | Immer selbst kurz ansehen |
| Community (Antworten) | 🟡 Teilweise | Lieber selbst machen, weil der Algorithmus echte Interaktion belohnt |

**Empfohlene Pipeline:**
```
n8n / Make / Python-Cronjob
  → LLM: Idee + Skript + Metadaten
  → Bild-/Video-API: Szenen
  → ElevenLabs: Voiceover
  → FFmpeg/Remotion: Schnitt + Untertitel
  → Ordner "review/"  ← DU schaust kurz drüber (2 Min.)
  → Upload-API: TikTok, IG, FB, YouTube (+ Snapchat)
```

---

## 4. Automatischer Upload: Optionen

### Option 1: Ein Dienst für alle Plattformen (am einfachsten)
| Dienst | TikTok | IG | FB | YouTube | Snapchat | Hinweis |
|---|---|---|---|---|---|---|
| **Upload-Post** | ✅ | ✅ | ✅ | ✅ | ❌ | Eine API für alle, ca. $8–126 pro Monat, 10 Uploads gratis |
| **ShortSync** | ✅ | ✅ | ? | ✅ | ✅ (Spotlight) | Speziell für Shorts, inklusive Snapchat |
| **Dash Social** | ✅ | ✅ | ✅ | ✅ | ✅ (Spotlight) | Eher Enterprise |
| Metricool, Buffer, Later, Publer | ✅ | ✅ | ✅ | ✅ | teils | Bedienung über die Oberfläche, Planung im Kalender |
| bundle.social | ✅ | ✅ | ✅ | ✅ | ⏳ „coming soon“ | |

👉 **Empfehlung:** **Upload-Post** (API) für TikTok, IG, FB und YouTube, plus **ShortSync** oder manueller Upload für Snapchat. Oder alles über einen Dienst mit Snapchat-Unterstützung, wenn dir eine Oberfläche reicht.

### Option 2: Offizielle APIs direkt (kostenlos, aber aufwendig)
- **YouTube:** YouTube Data API v3 (`videos.insert`). Ein Google-Cloud-Projekt und OAuth sind nötig. Ohne Audit sind Uploads oft „privat“ gesperrt, deshalb Audit beantragen.
- **Instagram und Facebook:** Meta Graph API (Content Publishing, Reels). Nötig sind ein Business-Account, eine Meta-App und App-Review.
- **TikTok:** Content Posting API. Ohne Audit sind Posts nur **privat** sichtbar. Für öffentliche Posts ist ein App-Audit nötig.
- **Snapchat:** Für Spotlight gibt es praktisch nur Partner-Zugang. Deshalb lieber ein Drittanbieter-Tool.

Ein Dienst aus Option 1 hat diese Freigaben schon, deshalb sparst du dir damit wochenlangen Aufwand.

### Beispiel-Skript
`scripts/upload.py` lädt ein Video über die Upload-Post-API auf mehrere Plattformen hoch (siehe Datei).

---

## 5. Regeln und Risiken (wichtig!)

- **KI-Label setzen.** TikTok verlangt ein Label für realistische KI-Bilder, -Audio und -Videos und setzt es teilweise automatisch. YouTube („Altered or synthetic content“) und Meta („AI info“) haben eigene Schalter.
- **Keine Deepfakes von echten Personen** ohne Erlaubnis. Das kann zur Sperre des Accounts führen. Vorsicht auch bei Promi-Edits (Rumpelstiltskin-Trend): klar als Parodie erkennbar machen.
- **Monetarisierung:** TikTok Creator Rewards und das YouTube Partner Program lehnen „unoriginelle oder massenproduzierte“ Inhalte ab. Füge eigene Elemente hinzu (Stimme, Story, Kommentar) und poste nicht 50 identische Template-Videos.
- **Musik und Urheberrecht:** Für automatisch hochgeladene Videos nur lizenzfreie oder eigene Musik verwenden.
- **Keine Bots für Likes oder Follower** und keine gescrapten Fremdvideos.
- In Deutschland: **Impressum** im Profil, wenn du kommerziell postest. Werbung kennzeichnen.

---

## Quellen
- https://www.yahoo.com/entertainment/articles/rumpelstiltskin-tip-toein-jordans-meme-171500100.html
- https://napoleoncat.com/blog/tiktok-trends/
- https://newengen.com/insights/october-tiktok-trends/
- https://ads.tiktok.com/business/library/TikTok_Next_2026_Trend_Report.pdf
- https://docs.upload-post.com/
- https://www.shortsync.app/resources/snapchat-spotlight-scheduling-guide-2026
- https://developer.dashsocial.com/api-reference/scheduler/snapchat/create-snapchat-scheduled-posts
- https://bundle.social/snapchat-api
- https://www.cinerads.com/blog/tiktok-ai-content-policy
