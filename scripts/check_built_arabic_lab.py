#!/usr/bin/env python3
"""Check that generated Arabic Lab pages contain their source metadata."""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site/dist"
MANIFEST = ROOT / "reports/source-manifest.json"
METADATA = ROOT / "scripts/elevations/data/arabic_lab_metadata.json"
INDEX = ROOT / "site/public/data/interview-lab.json"
HEADINGS = (
    "الفكرة ببساطة", "إجابة سريعة للانترفيو", "إجابة قوية للانترفيو",
    "لو الـ Interviewer دخل معاك في التفاصيل", "أسئلة ممكن تتسأل بعدها",
)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[`*]", "", html.unescape(value)).split())


def main() -> int:
    questions = json.loads(MANIFEST.read_text(encoding="utf-8"))["questions"]
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    index = json.loads(INDEX.read_text(encoding="utf-8"))["questions"]
    indexed = {row["id"]: row for row in index}
    errors = []
    groups = set()
    for q in questions:
        qid = q["id"]
        groups.add((q["code"], q["group"]))
        page = DIST / "ar/lab/questions" / qid.lower() / "index.html"
        if not page.is_file():
            errors.append(f"missing built Arabic page: {qid}")
            continue
        parser = TextExtractor()
        parser.feed(page.read_text(encoding="utf-8"))
        rendered = normalize(" ".join(parser.text))
        title = normalize(metadata[qid]["questionAr"])
        if title not in rendered:
            errors.append(f"Arabic question title missing from built page: {qid}")
        for heading in HEADINGS:
            if heading not in rendered:
                errors.append(f"{qid}: missing section {heading}")
        row = indexed.get(qid)
        if not row or row["questionAr"] != metadata[qid]["questionAr"]:
            errors.append(f"{qid}: public search index differs from metadata")
    for code in sorted({q["code"] for q in questions}):
        if not (DIST / "ar/lab/topics" / code.lower() / "index.html").is_file():
            errors.append(f"missing built Arabic topic page: {code}")
    print(f"{len(questions)} Arabic question pages checked; 21 topic pages; "
          f"{len(groups)} topic/group combinations; {len(errors)} errors")
    for error in errors[:20]:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
