---
name: clip-auswahl
description: Wählt aus dem Transkript eines langen Videos (Stream, Podcast) die viralsten Momente für Kurzclips aus und schneidet sie mit der Pipeline. Nutzen, wenn der User Clips aus einem Video machen will, besonders ohne ANTHROPIC_API_KEY.
---

# Clip-Auswahl

Nur für Material, das der User nutzen darf (offizielle Clipping-Kampagne oder eigene Videos). Bei unklaren Rechten nachfragen.

1. **Analysieren** (wenn noch kein Arbeitsordner existiert):
   ```
   python -m ki_videos clips analysieren <link-oder-datei> [--nische clips]
   ```
   Das legt `work/<nische>/<ordner>/` mit `transkript.txt` (Zeitstempel in Sekunden) an.

2. **Auswählen:** Lies `transkript.txt` und den Block der Nische in `config/niches.yaml` (`clip_min`, `clip_max`, `campaign_rules`). Wähle die stärksten Momente, standardmäßig 5:
   - Der erste Satz fesselt sofort (Pointe, Streit, Geständnis, überraschende Aussage).
   - Jeder Clip ist für sich verständlich, liegt zwischen `clip_min` und `clip_max` Sekunden und überschneidet sich nicht mit anderen.
   - Start und Ende liegen an Satzgrenzen.
   - Die Kampagnen-Regeln werden eingehalten.

   Schreib `work/<nische>/<ordner>/auswahl.json`:
   ```json
   {"clips": [{"start": 12.4, "end": 51.0, "title": "…", "description": "…", "hashtags": ["#…"], "reason": "…"}]}
   ```
   Titel max. 80 Zeichen, in der Sprache des Videos, keine falschen Versprechen.

3. **Schneiden:**
   ```
   python -m ki_videos clips schneiden work/<nische>/<ordner> [--nische clips]
   ```

4. **Prüfen:** Jeden Clip mit dem Skill `watch` ansehen (Hook, Untertitel synchron, nichts abgeschnitten). Gute Clips: `python -m ki_videos freigeben <ordner>`, schlechte: `verwerfen`.
