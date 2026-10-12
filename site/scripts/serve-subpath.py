"""Serve a built project-path snapshot for browser tests."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

BASE = "/android-interview-lab/"
DIST = Path(__file__).resolve().parent.parent / "dist"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def translate_path(self, path):
        parsed = urlsplit(path).path
        if not parsed.startswith(BASE):
            return str(DIST / "__missing__")
        return super().translate_path("/" + parsed[len(BASE):])


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 4539), Handler).serve_forever()
