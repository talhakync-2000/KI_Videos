"""Kommandozeile.

    python -m ki_videos nischen
    python -m ki_videos erstellen --nische saftladen [--thema "..."] [--anzahl 3]
    python -m ki_videos erstellen --nische saftladen --skript content/saftladen/folge-01.json
    python -m ki_videos erstellen --alle
    python -m ki_videos offen                       (wartet auf Prüfung)
    python -m ki_videos freigeben <ordner> | --alle-offenen   (auf nächsten Posting-Slot legen)
    python -m ki_videos plan                        (was wird wann hochgeladen?)
    python -m ki_videos hochladen --faellige        (für Aufgabenplanung/Cron alle 15 Min.)
    python -m ki_videos hochladen <ordner>          (sofort hochladen)
    python -m ki_videos verwerfen <ordner>          (schlechtes Video löschen)

    Clip-Modus (nur Material mit Erlaubnis, z. B. Clipping-Kampagnen):
    python -m ki_videos clips auto <link-oder-datei> [--nische clips] [--anzahl 5]
    python -m ki_videos clips analysieren <link-oder-datei>   (nur laden + transkribieren)
    python -m ki_videos clips auswaehlen <arbeitsordner> [--anzahl 5]
    python -m ki_videos clips schneiden <arbeitsordner>       (nach eigener Auswahl in auswahl.json)
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from . import pipeline

WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def _when(dt: datetime) -> str:
    return f"{WOCHENTAGE[dt.weekday()]} {dt:%d.%m. %H:%M}"


def main() -> None:
    # Windows-Konsole/Logdatei (cp1252) würde bei Emojis in Titeln abstürzen
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")
    load_dotenv()
    parser = argparse.ArgumentParser(prog="ki_videos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("nischen", help="Alle Nischen aus config/niches.yaml anzeigen")

    gen = sub.add_parser("erstellen", help="Neue Videos erzeugen")
    target = gen.add_mutually_exclusive_group(required=True)
    target.add_argument("--nische")
    target.add_argument("--alle", action="store_true", help="Für jeden aktiven Kanal ein Video")
    source = gen.add_mutually_exclusive_group()
    source.add_argument("--thema", help="Trend oder Thema vorgeben")
    source.add_argument("--skript", type=Path, nargs="+", help="Fertige Skript-JSON(s) rendern statt neu schreiben")
    gen.add_argument("--anzahl", type=int, default=1)
    gen.add_argument("--hochladen", action="store_true", help="Ohne Prüfung direkt hochladen")

    sub.add_parser("offen", help="Videos, die noch geprüft werden müssen")

    rel = sub.add_parser("freigeben", help="Geprüfte Videos auf den nächsten Posting-Slot legen")
    rel.add_argument("ordner", nargs="*", type=Path)
    rel.add_argument("--alle-offenen", action="store_true")
    rel.add_argument("--lokal", action="store_true",
                     help="Nicht sofort an Upload-Post schicken, sondern zur Posting-Zeit per Upload-Job")

    sub.add_parser("plan", help="Geplante Uploads anzeigen")

    up = sub.add_parser("hochladen", help="Videos hochladen")
    up.add_argument("ordner", nargs="*", type=Path)
    up_sel = up.add_mutually_exclusive_group()
    up_sel.add_argument("--alle-offenen", action="store_true", help="Alle geprüften sofort hochladen")
    up_sel.add_argument("--faellige", action="store_true", help="Freigegebene, deren Slot erreicht ist")

    cl = sub.add_parser("clips", help="Kurzclips aus langen Videos schneiden (Clipping)")
    cl.add_argument("aktion", choices=["auto", "analysieren", "auswaehlen", "schneiden"])
    cl.add_argument("quelle", help="Link/Datei (auto, analysieren) oder Arbeitsordner (auswaehlen, schneiden)")
    cl.add_argument("--nische", default="clips")
    cl.add_argument("--anzahl", type=int, default=5)

    rm = sub.add_parser("verwerfen", help="Schlechtes Video löschen (Serie macht dann an derselben Stelle weiter)")
    rm.add_argument("ordner", nargs="+", type=Path)

    args = parser.parse_args()
    failed = False

    if args.cmd == "nischen":
        for name, n in pipeline.load_niches().items():
            art = n.get("mode", "bilder") + (", Serie" if n.get("series") else "")
            if not n.get("active", True):
                art += ", pausiert"
            slots = ", ".join(n.get("posting_times", []))
            print(f"{name:18} {art:18} Profil: {n['upload_profile']:10} Slots: {slots:14} {', '.join(n['platforms'])}")

    elif args.cmd == "erstellen":
        names = pipeline.active_niches() if args.alle else [args.nische]
        jobs = [(name, None) for name in names for _ in range(args.anzahl)]
        if args.skript:
            if args.alle:
                parser.error("--skript geht nur zusammen mit --nische")
            jobs = [(args.nische, f) for f in args.skript]
        for name, script_file in jobs:
            try:
                folder = pipeline.generate(name, args.thema, script_file)
                if args.hochladen:
                    print(pipeline.upload_folder(folder))
            except Exception as e:  # ein Fehler soll die anderen Videos nicht stoppen
                failed = True
                print(f"[{name}] FEHLER: {e}", file=sys.stderr)

    elif args.cmd == "offen":
        for folder in pipeline.pending():
            print(folder / "video.mp4")

    elif args.cmd == "freigeben":
        for folder in pipeline.pending() if args.alle_offenen else args.ordner:
            slot, error = pipeline.schedule(folder, push=not args.lokal)
            if args.lokal:
                where = "lokal geplant"
            elif error:
                where = f"lokal geplant (Upload-Post-Fehler: {error})"
            else:
                where = "bei Upload-Post eingeplant"
            print(f"{_when(slot)}  {folder.parent.name:18} {folder.name}  -> {where}")

    elif args.cmd == "plan":
        for when, folder, where in pipeline.planned():
            print(f"{_when(when)}  {folder.parent.name:18} {where:11} {folder.name}")
        for folder in pipeline.by_status("partial"):
            missing = ", ".join(pipeline._read_meta(folder).get("failed_platforms", []))
            print(f"TEILWEISE FEHLGESCHLAGEN ({missing}): {folder}  -> erneut: hochladen {folder}")

    elif args.cmd == "hochladen":
        if args.faellige:
            folders = pipeline.due()
        elif args.alle_offenen:
            folders = pipeline.pending()
        else:
            folders = args.ordner
        for folder in folders:
            try:
                print(f"Lade hoch: {folder}")
                print(pipeline.upload_folder(folder))
                missing = pipeline._read_meta(folder).get("failed_platforms")
                if missing:
                    failed = True
                    print(f"FEHLGESCHLAGEN auf: {', '.join(missing)} -> erneut: hochladen {folder}", file=sys.stderr)
            except Exception as e:
                failed = True
                print(f"FEHLER bei {folder}: {e}", file=sys.stderr)

    elif args.cmd == "clips":
        from . import clips
        niche = pipeline.load_niches()[args.nische]
        if niche.get("mode") != "clip":
            parser.error(f"Kanal '{args.nische}' hat nicht mode: clip")
        if args.aktion == "auto":
            folders = clips.auto(args.quelle, args.nische, args.anzahl)
        elif args.aktion == "analysieren":
            work = clips.prepare(args.quelle, args.nische)
            lang = niche.get("language") if len(niche.get("language", "")) == 2 else None
            clips.transcribe(work, lang, niche.get("whisper_model", "small"))
            print(f"Arbeitsordner: {work}\nTranskript: {work / 'transkript.txt'}")
            folders = []
        elif args.aktion == "auswaehlen":
            clips.select(Path(args.quelle), args.nische, args.anzahl)
            print(f"Auswahl gespeichert: {Path(args.quelle) / 'auswahl.json'}")
            folders = []
        else:
            folders = clips.cut(Path(args.quelle), args.nische)
        for folder in folders:
            print(folder / "video.mp4")
        if folders:
            print("Jetzt prüfen, dann: python -m ki_videos freigeben --alle-offenen")

    elif args.cmd == "verwerfen":
        for folder in args.ordner:
            pipeline.discard(folder)
            print(f"Verworfen: {folder}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
