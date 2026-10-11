---
name: tagesproduktion
description: Tägliche Routine des ViralAI Managers - prüft den Upload-Plan, schreibt neue Folgen und Videos für alle Nischen, rendert sie mit der Pipeline, kontrolliert sie mit dem Watch-Plugin und gibt die guten zum Upload frei. Nutzen, wenn der User "Tagesproduktion", "neue Videos für heute" oder Ähnliches sagt.
---

# Tagesproduktion

Ziel: Für jede Nische sind immer die nächsten **3 Tage** an Posting-Slots mit geprüften Videos belegt.

## 1. Lage prüfen

```
python -m ki_videos nischen
python -m ki_videos plan
python -m ki_videos offen
```
Zähle pro Nische, wie viele Slots in den nächsten 3 Tagen belegt sind (Slots pro Tag stehen in `posting_times`). Schau in `trends/` nach Analysen der letzten 7 Tage.

## 2. Skripte schreiben

Für jeden fehlenden Slot schreibst du selbst ein Skript als JSON nach `content/<nische>/`, im Format der vorhandenen Dateien dort. Du brauchst dafür keinen Anthropic-API-Key, weil du die Skripte direkt schreibst.
- Regeln aus `ki_videos/script.py` (`BASE_RULES`, `MODE_RULES`) einhalten.
- Bei Figuren die `look`-Beschreibung wörtlich übernehmen und den `style` der Nische anhängen.
- **Serien** (`series: true`): `output/<nische>/history.json` lesen, an die letzte Folge anknüpfen, mit einem Cliffhanger enden, fortlaufend nummerieren.
- Trends aus `trends/` einbauen, wenn sie zur Nische passen.
- **SliceLab:** Objekt-Material-Paare nie wiederholen. Vorher `history.json` prüfen. Wünsche aus Kommentaren, die der User mitteilt, haben Vorrang.

## 3. Rendern

```
python -m ki_videos erstellen --nische <nische> --skript content/<nische>/<datei>.json [weitere ...]
```
Serien-Folgen immer in der richtigen Reihenfolge rendern. Bei Fehlern (API-Key, Guthaben, Netz) stoppen und dem User genau sagen, was fehlt.

## 4. Qualitätskontrolle

Sieh jedes neue Video (`python -m ki_videos offen`) mit dem Skill `watch` an und prüfe:
- Hook in den ersten 2 Sekunden da?
- Sehen die Figuren in allen Clips gleich aus?
- KI-Fehler: kaputte Hände oder Gesichter, Text im Bild, eingefrorene Clips?
- Ton: Ist der Dialog verständlich und in der richtigen Sprache, sind die Untertitel synchron?
- Nichts, was gegen Plattformregeln verstößt?

Schlecht: `python -m ki_videos verwerfen <ordner>`, das Skript verbessern und neu rendern (höchstens 2 Versuche pro Video, dann dem User melden).
Gut: `python -m ki_videos freigeben <ordner>`.

## 5. Bericht an den User

Kurz auf Deutsch:
- Was neu produziert und freigegeben wurde (mit Upload-Zeitpunkt aus `python -m ki_videos plan`)
- Was verworfen wurde und warum
- Geschätzte Kosten (Video-Modus ca. 1–3 $ pro Clip, Bilder-Modus ein paar Cent)
- Was der User tun muss: z. B. Trend-Sound in der App nachtragen, auf Kommentare antworten, Statistiken schicken

`freigeben` schickt jedes Video sofort an Upload-Post, das es zur Posting-Zeit veröffentlicht. Wenn `freigeben` „lokal geplant (Upload-Post-Fehler …)“ meldet, nenne dem User den Fehler. Die Windows-Aufgabe aus `setup/upload-job.ps1` holt es dann zur Posting-Zeit nach. Zeigt `plan` „TEILWEISE FEHLGESCHLAGEN“, mit `hochladen <ordner>` erneut versuchen.
