"""Kommandozeile.

    python -m ki_videos nischen
    python -m ki_videos erstellen --nische tier_fakten [--thema "Oktopus"] [--anzahl 3] [--hochladen]
    python -m ki_videos erstellen --alle
    python -m ki_videos offen
    python -m ki_videos hochladen output/tier_fakten/20261008-...   (oder --alle-offenen)
"""
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import pipeline


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(prog="ki_videos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("nischen", help="Alle Nischen aus config/niches.yaml anzeigen")

    gen = sub.add_parser("erstellen", help="Neue Videos erzeugen")
    target = gen.add_mutually_exclusive_group(required=True)
    target.add_argument("--nische")
    target.add_argument("--alle", action="store_true", help="Für jede Nische ein Video")
    gen.add_argument("--thema", help="Trend oder Thema vorgeben")
    gen.add_argument("--anzahl", type=int, default=1)
    gen.add_argument("--hochladen", action="store_true", help="Ohne Prüfung direkt hochladen")

    sub.add_parser("offen", help="Videos, die noch geprüft und hochgeladen werden müssen")

    up = sub.add_parser("hochladen", help="Geprüfte Videos hochladen")
    up.add_argument("ordner", nargs="*", type=Path)
    up.add_argument("--alle-offenen", action="store_true")

    args = parser.parse_args()

    if args.cmd == "nischen":
        for name, n in pipeline.load_niches().items():
            print(f"{name:20} Profil: {n['upload_profile']:15} Plattformen: {', '.join(n['platforms'])}")

    elif args.cmd == "erstellen":
        names = list(pipeline.load_niches()) if args.alle else [args.nische]
        failed = False
        for name in names:
            for _ in range(args.anzahl):
                try:
                    folder = pipeline.generate(name, args.thema)
                    if args.hochladen:
                        print(pipeline.upload_folder(folder))
                except Exception as e:  # eine fehlerhafte Nische soll die anderen nicht stoppen
                    failed = True
                    print(f"[{name}] FEHLER: {e}", file=sys.stderr)
        sys.exit(1 if failed else 0)

    elif args.cmd == "offen":
        for folder in pipeline.pending():
            print(folder / "video.mp4")

    elif args.cmd == "hochladen":
        folders = pipeline.pending() if args.alle_offenen else args.ordner
        for folder in folders:
            print(f"Lade hoch: {folder}")
            print(pipeline.upload_folder(folder))


if __name__ == "__main__":
    main()
