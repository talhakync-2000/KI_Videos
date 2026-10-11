# Wochenplan Woche 1

Reihenfolge = Upload-Reihenfolge. `freigeben` legt die Videos automatisch auf die nächsten freien Slots (Kapitalverbrechen 20:00, Sagenhaft 18:00).

**Rendern (Windows):**
```powershell
.venv\Scripts\python -m ki_videos erstellen --nische kapitalverbrechen --skript content\kapitalverbrechen\akte-001.json content\kapitalverbrechen\akte-002.json content\kapitalverbrechen\akte-003.json content\kapitalverbrechen\akte-004.json content\kapitalverbrechen\akte-005.json content\kapitalverbrechen\akte-006.json content\kapitalverbrechen\akte-007.json
.venv\Scripts\python -m ki_videos erstellen --nische sagenhaft --skript content\sagenhaft\folge-01.json content\sagenhaft\folge-02.json content\sagenhaft\folge-03.json content\sagenhaft\folge-04.json content\sagenhaft\folge-05.json content\sagenhaft\folge-06.json content\sagenhaft\folge-07.json
```
Danach jedes Video ansehen (oder `/tagesproduktion` prüfen lassen), dann `freigeben --alle-offenen`.

| Tag | Kanal | Uhrzeit | Skript | Titel |
|---|---|---|---|---|
| 1 | sagenhaft | 18:00 | `content/sagenhaft/folge-01.json` | Folge 1: Der Mann, der nicht nach Hause kam ⚔️ |
| 1 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-001.json` | Akte 001: Er verkaufte den Eiffelturm 🗼 |
| 2 | sagenhaft | 18:00 | `content/sagenhaft/folge-02.json` | Folge 2: Mein Name ist Niemand 👁️ |
| 2 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-002.json` | Akte 002: 50 % Gewinn in 45 Tagen 💸 |
| 3 | sagenhaft | 18:00 | `content/sagenhaft/folge-03.json` | Folge 3: Der Sack voller Winde 🌪️ |
| 3 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-003.json` | Akte 003: Eine Tulpe für ein Haus 🌷 |
| 4 | sagenhaft | 18:00 | `content/sagenhaft/folge-04.json` | Folge 4: Die Zauberin Kirke 🐖 |
| 4 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-004.json` | Akte 004: Selbst Newton verlor alles 📉 |
| 5 | sagenhaft | 18:00 | `content/sagenhaft/folge-05.json` | Folge 5: Die Reise ins Totenreich 💀 |
| 5 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-005.json` | Akte 005: Der Spieler, der Frankreich regierte 🎲 |
| 6 | sagenhaft | 18:00 | `content/sagenhaft/folge-06.json` | Folge 6: Das Lied der Sirenen 🎶 |
| 6 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-006.json` | Akte 006: Das Land, das es nie gab 🗺️ |
| 7 | sagenhaft | 18:00 | `content/sagenhaft/folge-07.json` | Folge 7: Die Rinder des Sonnengottes ☀️ |
| 7 | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-007.json` | Akte 007: Der Hauptmann von Köpenick 🎖️ |

Saftladen (3 Folgen) und SliceLab (5 Videos) liegen ebenfalls in `content/`, sind laut Marktanalyse aber erst später dran.

## Sonderfolge

| Datum | Kanal | Uhrzeit | Skript | Titel |
|---|---|---|---|---|
| **31.10. (Halloween)** | kapitalverbrechen | 20:00 | `content/kapitalverbrechen/akte-008.json` | Akte 008: Die Geister-Schwestern 👻 |

Akte 008 erst am 30.10. rendern und freigeben, damit sie genau auf Halloween fällt (`freigeben` nimmt den nächsten freien Slot).
