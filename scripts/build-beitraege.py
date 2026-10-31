
from pathlib import Path
from datetime import date, datetime
import json
import re

import yaml
import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "beitraege"
OUTPUT = ROOT / "content" / "beitraege.json"

def date_as_text(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value or "")

def read_entry(path):
    raw = path.read_text(encoding="utf-8-sig")

    match = re.match(
        r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z",
        raw,
        flags=re.DOTALL,
    )

    if not match:
        print(f"Übersprungen (kein Frontmatter): {path.name}")
        return None

    metadata = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()

    if not isinstance(metadata, dict):
        print(f"Übersprungen (ungültige Metadaten): {path.name}")
        return None

    photos = metadata.get("photos") or []
    if not isinstance(photos, list):
        photos = [photos]

    normalized_photos = []
    for photo in photos:
        if isinstance(photo, str):
            normalized_photos.append(photo)
        elif isinstance(photo, dict):
            image = photo.get("image")
            if image:
                normalized_photos.append(str(image))

    entry_date = date_as_text(metadata.get("date"))

    return {
        "id": path.stem,
        "title": str(metadata.get("title") or path.stem),
        "date": entry_date,
        "phase": str(metadata.get("phase") or ""),
        "body": body,
        "html": markdown.markdown(
            body,
            extensions=["extra", "sane_lists"],
        ),
        "photos": normalized_photos,
        "youtube": str(metadata.get("youtube") or ""),
    }

def main():
    entries = []

    if SOURCE.exists():
        for path in sorted(SOURCE.glob("*.md")):
            entry = read_entry(path)
            if entry is not None:
                entries.append(entry)

    entries.sort(
        key=lambda entry: (entry["date"], entry["id"]),
        reverse=True,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"{len(entries)} Bautagebuch-Beiträge verarbeitet.")
    print(f"Ausgabedatei: {OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
