import tempfile
import unittest
import zipfile
from pathlib import Path

from package_source import create_source_zip


class SourcePackageTests(unittest.TestCase):
    def test_excludes_caches_and_keeps_wrapper_with_relative_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "academy"
            root.mkdir()
            (root / "README.md").write_text("hello", encoding="utf-8")
            wrapper = root / "projects" / "lab" / "gradle" / "wrapper"
            wrapper.mkdir(parents=True)
            (wrapper / "gradle-wrapper.jar").write_bytes(b"official wrapper fixture")
            for hidden in (".git", ".gradle", ".kotlin", ".idea", ".astro", ".pytest_cache", "build", "__pycache__", "__MACOSX", "dist", "node_modules"):
                directory = root / hidden
                directory.mkdir()
                (directory / "junk.bin").write_bytes(b"junk")
            (root / ".DS_Store").write_bytes(b"junk")
            (root / "cached.pyc").write_bytes(b"junk")
            destination = root / "dist" / "academy-source.zip"
            create_source_zip(root, destination)
            with zipfile.ZipFile(destination) as archive:
                names = archive.namelist()
                self.assertEqual(["README.md", "projects/lab/gradle/wrapper/gradle-wrapper.jar"], names)
                self.assertEqual(b"official wrapper fixture", archive.read(names[1]))
                self.assertTrue(all(not name.startswith("/") for name in names))

    def test_excludes_generated_site_copies_but_keeps_site_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "academy"
            (root / "site" / "scripts").mkdir(parents=True)
            (root / "site" / "scripts" / "sync-content.mjs").write_text("source", encoding="utf-8")
            generated = root / "site" / "src" / "content" / "docs" / "lessons"
            generated.mkdir(parents=True)
            (generated / "kot-001.md").write_text("generated", encoding="utf-8")
            generated_mocks = root / "site" / "src" / "content" / "docs" / "mocks"
            generated_mocks.mkdir(parents=True)
            (generated_mocks / "mock-001.md").write_text("generated", encoding="utf-8")
            public_source = root / "site" / "public" / "source"
            public_source.mkdir(parents=True)
            (public_source / "Example.kt").write_text("generated", encoding="utf-8")
            destination = root / "dist" / "academy-source.zip"
            create_source_zip(root, destination)
            with zipfile.ZipFile(destination) as archive:
                self.assertEqual(["site/scripts/sync-content.mjs"], archive.namelist())

    def test_same_source_produces_identical_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "academy"
            root.mkdir()
            (root / "README.md").write_text("hello", encoding="utf-8")
            first = root / "dist" / "first.zip"
            second = root / "dist" / "second.zip"
            create_source_zip(root, first)
            create_source_zip(root, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()
