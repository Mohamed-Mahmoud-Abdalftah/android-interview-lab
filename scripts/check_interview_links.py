#!/usr/bin/env python3
"""Check canonical interview reference links and write a reproducible report.

Network failures and bot-blocked responses are reported as unverified, not as
confirmed broken links. A 404/410 is retried with GET before being classified.
"""
from __future__ import annotations

import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports/external-links.json"
HEADERS = {"User-Agent": "AndroidInterviewLab-LinkAudit/1.0 (+educational-content-review)"}


def reference_urls() -> dict[str, list[str]]:
    urls: dict[str, list[str]] = {}
    for path in sorted((ROOT / "Interview-Lab/questions").glob("*.md")):
        body = path.read_text(encoding="utf-8")
        section = body.split("## References and reviewed-on date\n", 1)
        if len(section) != 2:
            continue
        for url in re.findall(r"https://[^)\s]+", section[1]):
            urls.setdefault(url, []).append(path.stem)
    return urls


def request_status(url: str, method: str) -> tuple[int | None, str]:
    try:
        request = Request(url, headers=HEADERS, method=method)
        with urlopen(request, timeout=12) as response:
            return response.status, response.url
    except HTTPError as exc:
        return exc.code, exc.url
    except (URLError, TimeoutError, OSError) as exc:
        return None, str(exc)[:180]


def curl_status(url: str) -> tuple[int | None, str]:
    """Try curl when urllib times out; keep unavailable results unverified."""
    try:
        result = subprocess.run(
            ["curl", "--location", "--head", "--silent", "--show-error",
             "--max-time", "12", "--output", "/dev/null",
             "--write-out", "%{http_code}\n%{url_effective}", url],
            capture_output=True, text=True, timeout=14, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, "curl unavailable or timed out"
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) < 2 or not lines[0].isdigit():
        return None, result.stderr.strip()[:180] or "curl request failed"
    return int(lines[0]), lines[1]


def check(item: tuple[str, list[str]]) -> dict:
    url, ids = item
    status, destination = request_status(url, "HEAD")
    if status in (403, 405, 404, 410) or status is None:
        retry, retry_destination = request_status(url, "GET")
        if retry is not None:
            status, destination = retry, retry_destination
    if status is None:
        retry, retry_destination = curl_status(url)
        if retry is not None:
            status, destination = retry, retry_destination
    category = "ok" if status is not None and 200 <= status < 400 else (
        "broken" if status in (404, 410) else "unverified")
    return {"url": url, "questionIds": ids, "status": status,
            "category": category, "resolved": destination}


def main() -> int:
    urls = reference_urls()
    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = sorted(pool.map(check, urls.items()), key=lambda item: item["url"])
    counts = {name: sum(row["category"] == name for row in rows)
              for name in ("ok", "broken", "unverified")}
    report = {"references": sum(map(len, urls.values())), "uniqueUrls": len(urls),
              "counts": counts, "results": rows}
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{report['references']} citations, {len(urls)} unique URLs: "
          f"{counts['ok']} reachable, {counts['broken']} confirmed broken, "
          f"{counts['unverified']} unverified")
    for row in rows:
        if row["category"] == "broken":
            print(f"{row['status']} {row['url']} ({','.join(row['questionIds'])})")
    return 1 if counts["broken"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
