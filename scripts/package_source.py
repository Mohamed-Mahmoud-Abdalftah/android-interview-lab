#!/usr/bin/env python3
"""Create a reproducible, source-only academy ZIP with relative archive paths."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

EXCLUDED_PARTS = {".git", ".gradle", ".kotlin", ".idea", ".astro", ".pytest_cache", "build", "__pycache__", "__MACOSX", "dist", "node_modules"}
EXCLUDED_NAMES = {".DS_Store"}
GENERATED_SITE_PREFIXES = (
    "site/src/content/docs/lessons/", "site/src/content/docs/questions/", "site/src/content/docs/answers/",
    "site/src/content/docs/scenarios/", "site/src/content/docs/labs/", "site/src/content/docs/revision/",
    "site/src/content/docs/speaking/", "site/src/content/docs/mocks/", "site/src/content/docs/reference/", "site/src/data/academy.json",
    "site/public/data/", "site/public/source/",
    "site/src/content/docs/lab/questions/", "site/src/content/docs/lab/topics/", "site/src/content/docs/lab/index.md",
)


def is_generated_site_file(relative: str) -> bool:
    return any(relative.startswith(prefix) for prefix in GENERATED_SITE_PREFIXES)


def source_files(root: Path):
    """Return sorted source files; skip generated directories, metadata, and symlinks."""
    return sorted(
        (path for path in root.rglob("*")
         if path.is_file()
         and not path.is_symlink()
         and not (set(path.relative_to(root).parts) & EXCLUDED_PARTS)
         and path.name not in EXCLUDED_NAMES
         and not is_generated_site_file(path.relative_to(root).as_posix())
         and path.suffix.lower() not in {".zip", ".pyc"}),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def create_source_zip(root: Path, destination: Path) -> int:
    root = root.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = source_files(root)
    with ZipFile(destination, "w") as archive:
        for path in files:
            rel = path.relative_to(root).as_posix()
            info = ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if path.name == "gradlew" else 0o100644) << 16
            archive.writestr(info, path.read_bytes())
    return len(files)


if __name__ == "__main__":
    project = Path(__file__).resolve().parent.parent
    archive_path = project / "dist" / "Android-Interview-Mastery-source.zip"
    count = create_source_zip(project, archive_path)
    print(f"Created {archive_path.relative_to(project)} with {count} source files")
