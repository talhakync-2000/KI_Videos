---
name: trend-analyse
description: Analysiert virale Trend-Videos (TikTok, Reels, Shorts oder lokale Dateien) mit dem Watch-Plugin, erklärt, warum sie viral gehen, und überträgt das Muster in neue Skripte für unsere Nischen. Nutzen, wenn der User Links oder Videodateien zur Trend-Analyse schickt.
---

# Trend-Analyse

Eingabe: ein oder mehrere Links oder Dateipfade in den Argumenten oder in der Nachricht des Users.

## 1. Video ansehen

Sieh jedes Video mit dem Skill `watch` an (Plugin `watch@claude-video`, eingerichtet über das Repo claude-video-watch).
- Fehlt der Skill: sag dem User, dass er in seinem Repo `claude-video-watch` die Datei `install-deps.ps1` ausführen und Claude neu starten soll. Analysiere dann nichts geraten.
- Lässt sich ein Link nicht laden (Instagram und TikTok blockieren manchmal): bitte den User, das Video herunterzuladen und nach `trends/videos/` zu legen, dann die Datei ansehen.

## 2. Analyse nach festem Raster

Für jedes Video, mit Zeitstempeln:
1. **Hook (0–2 s):** Was passiert im ersten Bild, im ersten Ton und im ersten Satz? Warum scrollt man nicht weiter?
2. **Struktur und Tempo:** Länge, Anzahl der Schnitte, durchschnittliche Szenenlänge, Spannungsbogen, Ende (Loop, Cliffhanger, Pointe).
3. **Audio:** Trend-Sound, Stimme (welcher Ton), Soundeffekte, Musik. Wenn es ein Trend-Sound ist: Name notieren. Den Sound kann man nur in der App hinzufügen, die Pipeline kann ihn nicht einbauen.
4. **Thema und Emotion:** Welches Gefühl wird ausgelöst (Schadenfreude, Neugier, Empörung, Entspannung, Staunen)?
5. **Format:** Serie, Einzelvideo, Loop, Mitmach-Format? Feste Figuren?
6. **Interaktion:** Was bringt die Leute zum Kommentieren, Teilen oder Folgen? Wenn sichtbar, die Top-Kommentare lesen.
7. **Caption und Hashtags:** Wörtlich notieren.
8. **Warum viral:** 3 konkrete Hypothesen, nach Gewicht sortiert.

## 3. Auf unsere Nischen übertragen

Lies `config/niches.yaml` und `branding/BRANDING.md`. Für jede passende Nische (`saftladen`, `slicelab`, `sagenhaft`):
- Was übernehmen wir konkret (Hook-Muster, Tempo, Dialog-Stil, Ende)?
- Was übernehmen wir nicht (Kopie, Urheberrecht, Regelverstöße)?

Schreib dann 1–3 neue Skripte als JSON nach `content/<nische>/`, im gleichen Format wie die vorhandenen Dateien dort. Lies vorher eine davon als Vorlage. Regeln:
- Halte dich an die Regeln in `ki_videos/script.py` (`BASE_RULES` und `MODE_RULES` für den Modus der Nische).
- Bei Figuren aus `characters` übernimmst du die `look`-Beschreibung wörtlich in jeden `visual_prompt` und hängst den `style` der Nische an.
- **Serien:** Lies `output/<nische>/history.json` und die neuesten Dateien in `content/<nische>/`. Die neue Folge knüpft an die letzte an. Nummeriere fortlaufend (`folge-NN.json`, Titel „Folge N: …“).
- Kopiere keine fremden Figuren, Marken, Dialoge oder Sounds.

## 4. Speichern

Leg die Analyse unter `trends/JJJJ-MM-TT-<kurzname>.md` ab, mit der Gliederung aus `trends/VORLAGE.md`. Unter „Umsetzung“ verlinkst du die neu geschriebenen Skripte.

## 5. Antwort an den User

Kurz und auf Deutsch: die 3 wichtigsten Gründe, warum das Video viral ging, welche Skripte neu entstanden sind, und der Befehl zum Rendern:
`python -m ki_videos erstellen --nische <nische> --skript content/<nische>/<datei>.json`
