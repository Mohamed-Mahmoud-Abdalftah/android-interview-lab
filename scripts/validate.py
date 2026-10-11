#!/usr/bin/env python3
"""Validate the academy's authored catalog and local navigation.

This is a structural check. A human reviewer must still judge technical
accuracy, conceptual dependencies, source relevance, and answer quality.
"""

import json
import re
import sys
from collections import Counter
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ITEM_TYPES = {"lesson", "extended_topic", "question", "scenario", "coding_challenge", "mock_pack"}
STATUSES = {"planned", "draft", "reviewed"}
SOURCE_STATUSES = {"verified", "pending_verification"}
CODE_STATUSES = {"tested", "not_run", "not_applicable"}
LESSON_KEYS = {
    "id", "title", "module", "tier", "estimated_minutes", "prerequisite_ids",
    "learning_outcomes", "status", "last_source_checked", "source_urls",
    "example_paths", "question_ids", "code_verification",
}
QUESTION_KEYS = {"id", "lesson_id", "topic", "difficulty", "style", "expected_minutes", "status"}
LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")
HTML_HREF = re.compile(r'<a\b[^>]*\bhref\s*=\s*(["\'])(.*?)\1', re.IGNORECASE)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
FRONT_KEY = re.compile(r"^([a-z_]+):(?:\s*(.*))?$")
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
SKIP_PARTS = {".git", ".gradle", ".kotlin", ".idea", ".astro", ".pytest_cache", "build", "dist", "__pycache__", "__MACOSX", "node_modules"}
SKIP_NAMES = {".DS_Store"}
GENERATED_SITE_PREFIXES = (
    "site/src/content/docs/lessons/", "site/src/content/docs/questions/", "site/src/content/docs/answers/",
    "site/src/content/docs/scenarios/", "site/src/content/docs/labs/", "site/src/content/docs/revision/",
    "site/src/content/docs/speaking/", "site/src/content/docs/mocks/", "site/src/content/docs/reference/", "site/src/data/academy.json",
    "site/public/data/", "site/public/source/",
    "Interview-Lab/", "site/src/content/docs/lab/", "site/src/content/docs/404.md",
)
LESSON_SECTIONS = {
    "mental model": r"mental model|نموذج",
    "mechanism or trace": r"mechanism|trace|execution|التنفيذ",
    "wrong and corrected implementation": r"wrong|correct|implementation|تصحيح",
    "tests and failure cases": r"test|failure case|اختبار",
    "interview explanation": r"interview|speaking|مقابلة",
    "senior follow-ups": r"follow.?up|متابعة",
    "misconceptions or revision": r"misconception|revision|self.check|مراجعة",
}


def source_files(root: Path):
    """Files that belong in the source-only inventory."""
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
        and path.name not in SKIP_NAMES
        and not any(path.relative_to(root).as_posix().startswith(prefix) for prefix in GENERATED_SITE_PREFIXES)
        and path.suffix not in {".pyc", ".zip"}
    }


def value(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inside = raw[1:-1].strip()
        return [part.strip().strip("\"'") for part in inside.split(",")] if inside else []
    return raw.strip("\"'")


def front_matter(path: Path):
    """Parse the deliberately small YAML subset used by academy documents."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}, content, ["missing front matter"]
    end = content.find("\n---\n", 4)
    if end < 0:
        return {}, content, ["unterminated front matter"]
    block = content[4:end]
    fields = {}
    errors = []
    current_list = None
    for number, line in enumerate(block.splitlines(), 2):
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list is None:
                errors.append(f"front matter line {number}: list item without key")
            else:
                fields[current_list].append(value(line[4:]))
            continue
        match = FRONT_KEY.fullmatch(line)
        if not match:
            errors.append(f"front matter line {number}: invalid syntax")
            current_list = None
            continue
        key, raw = match.groups()
        if key in fields:
            errors.append(f"duplicate front matter key {key}")
        if raw is None or not raw.strip():
            fields[key] = []
            current_list = key
        else:
            fields[key] = value(raw)
            current_list = None
    return fields, content[end + 5:], errors


def local_path(root: Path, base: Path, target: str):
    if not isinstance(target, str) or not target.strip():
        return None
    resolved = (base / unquote(target)).resolve()
    return resolved if resolved.is_relative_to(root.resolve()) else None


def clean_markdown(content: str):
    """Ignore fenced examples when finding headings and links."""
    lines = []
    fence = None
    for line in content.splitlines():
        found = re.match(r"^\s*(`{3,}|~{3,})", line)
        if found:
            marker = found.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def heading_anchors(content: str):
    counts = Counter()
    anchors = set()
    for match in HEADING.finditer(clean_markdown(content)):
        title = re.sub(r"<[^>]+>", "", match.group(1))
        title = re.sub(r"[^\w\- ]", "", title.lower()).strip().replace(" ", "-")
        slug = f"{title}-{counts[title]}" if counts[title] else title
        anchors.add(slug)
        counts[title] += 1
    anchors.update(re.findall(r'<[a-z][^>]*\bid\s*=\s*["\']([^"\']+)', clean_markdown(content), re.IGNORECASE))
    anchors.update(re.findall(r'<a\s+name\s*=\s*["\']([^"\']+)', clean_markdown(content), re.IGNORECASE))
    return anchors


def links_from(content: str):
    visible = clean_markdown(content)
    markdown = [match.group(1).strip("<>") for match in LINK.finditer(visible)]
    html = [unescape(match.group(2)) for match in HTML_HREF.finditer(visible)]
    return markdown + html


class RTLStructure(HTMLParser):
    """Check semantic direction in authored HTML blocks, not rendered layout."""

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.errors = []

    def ancestor(self, names):
        return next(((tag, attrs) for tag, attrs in reversed(self.stack) if tag in names), None)

    def rtl_ancestor(self):
        return next(((tag, attrs) for tag, attrs in reversed(self.stack) if attrs.get("dir") == "rtl"), None)

    def handle_starttag(self, tag, raw_attrs):
        attrs = dict(raw_attrs)
        ident = attrs.get("id")
        if ident:
            if ident in self.ids:
                self.errors.append(f"duplicate HTML ID {ident}")
            self.ids.add(ident)
        if tag == "code" and self.rtl_ancestor() and attrs.get("dir") != "ltr":
            self.errors.append("inline code needs dir=ltr inside Arabic block")
        if tag not in self.VOID_TAGS:
            self.stack.append((tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f"unbalanced HTML closing tag </{tag}>")
            return
        self.stack.pop()

    def handle_data(self, data):
        if not data.strip() or not self.stack:
            return
        if not self.ancestor({"code"}) and re.search(r"\*\*|`|\[[^\]]+\]\([^)]+\)", data):
            self.errors.append("Markdown syntax inside raw HTML")
        if not re.search(r"[\u0600-\u06ff]", data):
            anchor = self.ancestor({"a"})
            if anchor and self.rtl_ancestor() and re.search(r"[A-Za-z]", data) and anchor[1].get("dir") != "ltr":
                self.errors.append("English link needs dir=ltr inside Arabic block")
            return
        paragraph = self.ancestor({"p"})
        if paragraph and (paragraph[1].get("dir"), paragraph[1].get("lang")) != ("rtl", "ar"):
            self.errors.append("Arabic paragraph needs dir=rtl and lang=ar")
        heading = self.ancestor({"h1", "h2", "h3", "h4", "h5", "h6"})
        if heading and (heading[1].get("dir"), heading[1].get("lang")) != ("rtl", "ar"):
            self.errors.append("Arabic HTML heading needs dir=rtl and lang=ar")
        if heading and not heading[1].get("id"):
            self.errors.append("Arabic HTML heading needs stable id")
        list_node = self.ancestor({"ol", "ul"})
        if list_node and (list_node[1].get("dir"), list_node[1].get("lang")) != ("rtl", "ar"):
            self.errors.append("Arabic list needs dir=rtl and lang=ar")
        table = self.ancestor({"table"})
        if table and (table[1].get("dir"), table[1].get("lang")) != ("rtl", "ar"):
            self.errors.append("Arabic table needs dir=rtl and lang=ar")


def check_rtl_structure(root, errors):
    for relative in sorted(source_files(root)):
        if not relative.endswith(".md"):
            continue
        content = (root / relative).read_text(encoding="utf-8")
        if re.search(r"[\u202a-\u202e\u2066-\u2069]", content):
            errors.append(f"{relative}: invisible bidi control character")
        visible = clean_markdown(content)
        html_lines = [line for line in visible.splitlines() if re.match(r"^\s*</?[a-z][^>]*>", line, re.IGNORECASE)]
        if not html_lines:
            continue
        parser = RTLStructure()
        parser.feed("\n".join(html_lines))
        parser.close()
        errors.extend(f"{relative}: {issue}" for issue in dict.fromkeys(parser.errors))
        if parser.stack:
            errors.append(f"{relative}: unbalanced HTML opening tag <{parser.stack[-1][0]}>")


def normalized_list(fields, key):
    result = fields.get(key)
    return result if isinstance(result, list) else None


def positive_integer(fields, key):
    raw = fields.get(key)
    return isinstance(raw, str) and raw.isdecimal() and int(raw) > 0


def check_manifest(root, items, errors):
    by_id = {}
    by_path = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"manifest item {index}: expected object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ID_PATTERN.fullmatch(ident):
            errors.append(f"manifest item {index}: invalid ID {ident}")
            continue
        if ident in by_id:
            errors.append(f"duplicate ID: {ident}")
        else:
            by_id[ident] = item
        if item.get("type") not in ITEM_TYPES:
            errors.append(f"{ident}: invalid type {item.get('type')}")
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{ident}: invalid status {status}")
        source_status = item.get("source_status")
        if source_status not in SOURCE_STATUSES or (status == "planned" and source_status != "pending_verification"):
            errors.append(f"{ident}: invalid source_status {source_status} for {status}")
        if status == "reviewed" and source_status != "verified":
            errors.append(f"{ident}: reviewed item needs verified source_status")
        if item.get("code_verification") not in CODE_STATUSES:
            errors.append(f"{ident}: invalid code_verification {item.get('code_verification')}")
        rel = item.get("path")
        if not isinstance(rel, str) or not rel.endswith(".md") or local_path(root, root, rel) is None:
            errors.append(f"{ident}: invalid path {rel}")
        elif rel in by_path:
            errors.append(f"duplicate manifest path: {rel} for {ident} and {by_path[rel]}")
        else:
            by_path[rel] = ident
        for key in ("prerequisites", "question_ids", "example_paths", "source_urls"):
            entries = item.get(key)
            if not isinstance(entries, list) or any(not isinstance(entry, str) or not entry for entry in entries):
                errors.append(f"{ident}: invalid {key} list")
            elif len(entries) != len(set(entries)):
                errors.append(f"{ident}: duplicate {key}")
        if status == "planned" and isinstance(rel, str) and (root / rel).exists():
            errors.append(f"{ident}: planned path already exists {rel}")
        if status in {"draft", "reviewed"} and isinstance(rel, str) and not (root / rel).is_file():
            errors.append(f"{ident}: missing {status} path {rel}")
        if status == "reviewed" and item.get("type") != "question" and not item.get("source_urls"):
            errors.append(f"{ident}: reviewed item has no source_urls")

    for ident, item in by_id.items():
        prerequisites = item.get("prerequisites")
        if not isinstance(prerequisites, list):
            continue
        for prerequisite in prerequisites:
            if prerequisite not in by_id:
                errors.append(f"{ident}: unknown prerequisite {prerequisite}")
            elif by_id[prerequisite].get("type") not in {"lesson", "extended_topic"}:
                errors.append(f"{ident}: invalid prerequisite type {prerequisite}")
            elif prerequisite == ident:
                errors.append(f"{ident}: self prerequisite")
            elif item.get("type") == "lesson" and by_id[prerequisite].get("type") == "lesson":
                before, after = by_id[prerequisite].get("day"), item.get("day")
                if isinstance(before, int) and isinstance(after, int) and before >= after:
                    errors.append(f"{ident}: prerequisite {prerequisite} is not earlier in the learning sequence")
        if item.get("type") in {"lesson", "extended_topic"} and isinstance(item.get("question_ids"), list):
            for question_id in item["question_ids"]:
                if question_id not in by_id or by_id[question_id].get("type") != "question":
                    errors.append(f"{ident}: unknown question_id {question_id}")

    visiting, visited = set(), set()
    def walk(ident, stack):
        if ident in visiting:
            errors.append("prerequisite cycle: " + " -> ".join(stack + [ident]))
            return
        if ident in visited:
            return
        visiting.add(ident)
        for dependency in by_id[ident].get("prerequisites", []):
            if isinstance(dependency, str) and dependency in by_id:
                walk(dependency, stack + [ident])
        visiting.remove(ident)
        visited.add(ident)
    for ident in by_id:
        walk(ident, [])

    lessons = [item for item in by_id.values() if item.get("type") == "lesson"]
    days = [item.get("day") for item in lessons]
    if any(not isinstance(day, int) or day < 1 for day in days) or len(days) != len(set(days)):
        errors.append("lesson days must be unique positive integers")
    for item in lessons:
        day = item.get("day")
        if not isinstance(day, int):
            continue
        previous = next((other.get("id") for other in lessons if other.get("day") == day - 1), None)
        if item.get("sequence_previous", "<missing>") != previous:
            errors.append(f"{item['id']}: sequence_previous must be {previous}")
    if days and set(days) != set(range(1, len(days) + 1)):
        errors.append("lesson days must form a continuous learning sequence")
    return by_id


def check_front_matter(root, items, errors):
    documents = {}
    by_front_id = {}
    expected_answers = {}
    for item in items.values():
        if item.get("type") == "question" and item.get("status") in {"draft", "reviewed"}:
            answer = item.get("answer_path")
            if isinstance(answer, str):
                expected_answers[answer] = item["id"]
    for relative in sorted(source_files(root)):
        if not relative.endswith(".md"):
            continue
        path = root / relative
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            continue
        fields, body, issues = front_matter(path)
        documents[relative] = (fields, body)
        errors.extend(f"{relative}: {issue}" for issue in issues)
        ident = fields.get("id")
        if not isinstance(ident, str) or not ID_PATTERN.fullmatch(ident):
            errors.append(f"{relative}: invalid front matter ID {ident}")
            continue
        if ident in by_front_id:
            errors.append(f"duplicate front matter ID: {ident} in {relative} and {by_front_id[ident]}")
        by_front_id[ident] = relative
        owner = items.get(ident)
        if owner and owner.get("path") != relative:
            errors.append(f"{relative}: front matter ID {ident} belongs to {owner.get('path')}")
        elif not owner and expected_answers.get(relative) != ident.removesuffix("-ANSWER"):
            errors.append(f"{relative}: unregistered front matter ID {ident}")

    for ident, item in items.items():
        if item.get("status") not in {"draft", "reviewed"}:
            continue
        relative = item.get("path")
        if not isinstance(relative, str) or relative not in documents:
            if isinstance(relative, str) and (root / relative).is_file():
                errors.append(f"{ident}: missing front matter in {relative}")
            continue
        fields, body = documents[relative]
        if fields.get("id") != ident:
            errors.append(f"{ident}: front matter ID {fields.get('id')} does not match manifest")
        if fields.get("status") != item.get("status"):
            errors.append(f"{ident}: front matter status does not match manifest")
        if len(body.strip()) < (80 if item.get("status") == "reviewed" else 30) or re.search(r"\b(?:TODO|TBD)\b", body):
            errors.append(f"{ident}: {item['status']} content is empty or has placeholder")
        kind = item.get("type")
        required = LESSON_KEYS if kind in {"lesson", "extended_topic"} else QUESTION_KEYS if kind == "question" else {"id", "lesson_id", "status"} if kind in {"scenario", "coding_challenge"} else {"id", "status"}
        missing = required - fields.keys()
        if missing:
            errors.append(f"{ident}: missing front matter {sorted(missing)}")
        if kind in {"lesson", "extended_topic"}:
            check_lesson(root, item, fields, body, errors)
        if kind == "question":
            check_question(root, item, fields, body, items, documents, errors)
        if kind in {"scenario", "coding_challenge"}:
            lesson_id = fields.get("lesson_id")
            if lesson_id not in items or items[lesson_id].get("type") not in {"lesson", "extended_topic"} or lesson_id not in item.get("prerequisites", []):
                errors.append(f"{ident}: invalid lesson_id {lesson_id}")
            if fields.get("code_verification") != item.get("code_verification"):
                errors.append(f"{ident}: front matter code_verification does not match manifest")
        for example in item.get("example_paths", []):
            path = local_path(root, root, example)
            if not path or not path.is_file():
                errors.append(f"{ident}: missing example {example}")
        if item.get("code_verification") == "tested":
            check_test_evidence(root, item, body, errors)
    return documents


def check_lesson(root, item, fields, body, errors):
    ident = item["id"]
    if fields.get("title") != item.get("title"):
        errors.append(f"{ident}: front matter title does not match manifest")
    if fields.get("module") != Path(item["path"]).parent.as_posix() and Path(item["path"]).parent != Path("."):
        errors.append(f"{ident}: front matter module does not match path")
    if fields.get("tier") not in {"Core", "Important", "Advanced", "Specialist"}:
        errors.append(f"{ident}: invalid front matter tier")
    if not positive_integer(fields, "estimated_minutes"):
        errors.append(f"{ident}: invalid front matter estimated_minutes")
    if not normalized_list(fields, "learning_outcomes") or any(not outcome.strip() for outcome in fields["learning_outcomes"]):
        errors.append(f"{ident}: invalid front matter learning_outcomes")
    for key, manifest_key in (("prerequisite_ids", "prerequisites"), ("question_ids", "question_ids"), ("source_urls", "source_urls")):
        if normalized_list(fields, key) != item.get(manifest_key):
            errors.append(f"{ident}: front matter {key} does not match manifest")
    if fields.get("code_verification") != item.get("code_verification"):
        errors.append(f"{ident}: front matter code_verification does not match manifest")
    if fields.get("source_status") is not None and fields.get("source_status") != item.get("source_status"):
        errors.append(f"{ident}: front matter source_status does not match manifest")
    checked = fields.get("last_source_checked")
    try:
        date.fromisoformat(checked)
    except (ValueError, TypeError):
        errors.append(f"{ident}: invalid front matter last_source_checked")
    front_examples = normalized_list(fields, "example_paths")
    if front_examples is None:
        errors.append(f"{ident}: invalid front matter example_paths")
    else:
        normalized = []
        for path in front_examples:
            resolved = local_path(root, root / Path(item["path"]).parent, path)
            normalized.append(resolved.relative_to(root).as_posix() if resolved else None)
        if sorted(normalized, key=str) != sorted(item.get("example_paths", []), key=str):
            errors.append(f"{ident}: front matter example_paths do not match manifest")
    if item.get("status") == "reviewed":
        headings = [match.group(1).lower() for match in HEADING.finditer(clean_markdown(body))]
        for label, pattern in LESSON_SECTIONS.items():
            if not any(re.search(pattern, heading) for heading in headings):
                errors.append(f"{ident}: missing lesson section {label}")


def check_question(root, item, fields, body, items, documents, errors):
    ident = item["id"]
    lesson_id = fields.get("lesson_id")
    if lesson_id not in items or items[lesson_id].get("type") not in {"lesson", "extended_topic"} or lesson_id not in item.get("prerequisites", []):
        errors.append(f"{ident}: invalid lesson_id {lesson_id}")
    elif ident not in items[lesson_id].get("question_ids", []):
        errors.append(f"{ident}: absent from parent lesson question_ids")
    if not fields.get("topic") or fields.get("difficulty") not in {"foundational", "intermediate", "senior"} or not fields.get("style") or not positive_integer(fields, "expected_minutes"):
        errors.append(f"{ident}: invalid question front matter values")
    answer_path = item.get("answer_path")
    if not isinstance(answer_path, str) or not (root / answer_path).is_file():
        errors.append(f"{ident}: missing answer {answer_path}")
        return
    if answer_path not in documents:
        errors.append(f"{ident}: missing answer front matter")
        return
    answer_fields, answer_body = documents[answer_path]
    if answer_fields.get("id") != ident + "-ANSWER" or answer_fields.get("question_id") != ident or answer_fields.get("status") != item.get("status"):
        errors.append(f"{ident}: answer relationship mismatch")
    linked = {local_path(root, root / Path(item["path"]).parent, urlsplit(link).path) for link in links_from(body) if not urlsplit(link).scheme}
    if (root / answer_path).resolve() not in linked:
        errors.append(f"{ident}: question does not link its complete answer")
    if len(answer_body.strip()) < 120 or "Spoken answer" not in answer_body:
        errors.append(f"{ident}: incomplete model answer")
    followups = re.findall(r"^\*\*Follow-up\s+\d+:\*\*\s*(.*?)\?\s+(.*)$", answer_body, re.MULTILINE | re.IGNORECASE)
    if len(followups) < 2:
        errors.append(f"{ident}: answer has fewer than two follow-ups")
    for question, response in followups:
        if len(re.findall(r"\w+", question)) < 3 or len(re.findall(r"\w+", response)) < 8:
            errors.append(f"{ident}: incomplete follow-up answer")
            break


def check_test_evidence(root, item, body, errors):
    ident = item["id"]
    examples = item.get("example_paths", [])
    test_paths = list(examples)
    test_paths.extend(urlsplit(link).path for link in links_from(body))
    if not any(re.search(r"(?:^|/)(?:src/test/|[^/]*[Tt]est[^/]*\.(?:kt|java|py)$|LabChecks\.kt$)", path) for path in test_paths):
        errors.append(f"{ident}: tested content has no referenced test source")
    evidence = item.get("verification_evidence")
    path = local_path(root, root, evidence) if isinstance(evidence, str) else None
    if not path or not path.is_file():
        errors.append(f"{ident}: missing verification evidence {evidence}")
        return
    record = path.read_text(encoding="utf-8")
    current = re.search(r"^##\s+Current\b.*$", record, re.MULTILINE | re.IGNORECASE)
    if current:
        next_section = re.search(r"^##\s+", record[current.end():], re.MULTILINE)
        record = record[current.end():current.end() + next_section.start()] if next_section else record[current.end():]
    def count(pattern):
        found = re.search(pattern, record, re.IGNORECASE)
        return int(next(group for group in found.groups() if group is not None)) if found else None
    test_count = count(r"\b(\d+)\s+tests?\b|\btests\s*=\s*(\d+)\b")
    failures = count(r"\b(\d+)\s+failed\b|\bfailures\s*=\s*(\d+)\b")
    skipped = count(r"\b(\d+)\s+skipped\b|\bskipped\s*=\s*(\d+)\b")
    if not (re.search(r"\./gradlew[^\n]*\btest\b", record) and "BUILD SUCCESSFUL" in record
            and test_count is not None and test_count > 0 and failures == 0
            and (skipped is None or skipped < test_count)):
        errors.append(f"{ident}: verification evidence lacks successful test command and count")


def check_local_links(root, errors):
    for relative in sorted(source_files(root)):
        if not relative.endswith(".md"):
            continue
        path = root / relative
        for target in links_from(path.read_text(encoding="utf-8")):
            parts = urlsplit(target)
            if parts.scheme in {"http", "https", "mailto"}:
                continue
            if parts.scheme:
                errors.append(f"invalid link scheme: {relative} -> {target}")
                continue
            destination = local_path(root, path.parent, parts.path) if parts.path else path
            if not destination or not destination.exists():
                errors.append(f"broken link: {relative} -> {target}")
            elif parts.fragment and destination.is_file() and destination.suffix.lower() == ".md":
                fragment = unquote(parts.fragment).lower()
                if fragment not in heading_anchors(destination.read_text(encoding="utf-8")):
                    errors.append(f"broken anchor: {relative} -> {target}")


def check_registries(root, items, documents, errors):
    reviewed = {ident: item for ident, item in items.items() if item.get("type") == "question" and item.get("status") == "reviewed"}
    if not reviewed:
        return
    folder = root / "Interview-Question-Bank"
    for name in ("BY-TOPIC.md", "BY-DIFFICULTY.md", "BY-INTERVIEW-STYLE.md"):
        path = folder / name
        if not path.is_file():
            errors.append(f"missing question registry {path.relative_to(root)}")
            continue
        counts = Counter()
        for line in path.read_text(encoding="utf-8").splitlines():
            linked = []
            for link in links_from(line):
                target = urlsplit(link)
                destination = local_path(root, path.parent, target.path) if not target.scheme else None
                if destination:
                    for ident, item in reviewed.items():
                        if destination == (root / item["path"]).resolve():
                            linked.append(ident)
            for ident in linked:
                counts[ident] += 1
                item = reviewed[ident]
                answer = (root / item.get("answer_path", "")).resolve()
                destinations = {local_path(root, path.parent, urlsplit(link).path) for link in links_from(line) if not urlsplit(link).scheme}
                if answer not in destinations:
                    errors.append(f"{name}: {ident} has no matching answer link")
                if name != "BY-TOPIC.md":
                    fields = documents.get(item["path"], ({}, ""))[0]
                    category = line.lstrip("- ").split(":", 1)[0].strip().lower().replace(" ", "-")
                    expected = fields.get("difficulty" if name == "BY-DIFFICULTY.md" else "style")
                    if category != expected:
                        errors.append(f"{name}: {ident} category {category} disagrees with front matter {expected}")
        for ident, count in counts.items():
            if count > 1:
                errors.append(f"duplicate registry entry: {ident} in {name}")
        for ident in reviewed:
            if counts[ident] == 0:
                errors.append(f"{name}: missing registry entry {ident}")


def coverage_path(cell):
    match = LINK.search(cell)
    if match:
        return match.group(1).strip("<>")
    match = re.search(r"`([^`]+)`", cell)
    return match.group(1) if match else None


def check_coverage(root, items, errors):
    path = root / "COVERAGE-MATRIX.md"
    if not path.is_file():
        errors.append("missing COVERAGE-MATRIX.md")
        return
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 10 or not ID_PATTERN.fullmatch(cells[0]):
            continue
        ident = cells[0]
        if ident in rows:
            errors.append(f"duplicate coverage row {ident}")
        rows[ident] = cells
    expected = {ident: item for ident, item in items.items() if item.get("type") in {"lesson", "extended_topic"}}
    for ident, item in expected.items():
        cells = rows.get(ident)
        if not cells:
            errors.append(f"coverage missing row {ident}")
            continue
        if coverage_path(cells[5]) != item.get("path"):
            errors.append(f"{ident}: coverage path disagrees with manifest")
        if cells[9] != item.get("status"):
            errors.append(f"{ident}: coverage status disagrees with manifest")
        prereq = [] if cells[3].lower() == "none" else [part.strip() for part in cells[3].split(",")]
        if sorted(prereq) != sorted(item.get("prerequisites", [])):
            errors.append(f"{ident}: coverage prerequisites disagree with manifest")
    for ident in rows.keys() - expected.keys():
        errors.append(f"coverage unregistered row {ident}")


def check_inventory(root, errors):
    path = root / "FILE-INVENTORY.md"
    if not path.is_file():
        errors.append("missing FILE-INVENTORY.md")
        return
    content = path.read_text(encoding="utf-8")
    match = re.search(r"```text\n(.*?)\n```", content, re.DOTALL)
    if not match:
        errors.append("inventory missing fenced path list")
        return
    listed = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    counts = Counter(listed)
    for name, count in counts.items():
        if count > 1:
            errors.append(f"duplicate inventory entry {name}")
    actual = source_files(root)
    errors.extend(f"inventory missing file {name}" for name in sorted(actual - counts.keys()))
    errors.extend(f"inventory stale file {name}" for name in sorted(counts.keys() - actual))
    count_match = re.search(r"\b(?:These|Total:)\s+(\d+)\s+files\b", content)
    if count_match and int(count_match.group(1)) != len(actual):
        errors.append(f"inventory count {count_match.group(1)} disagrees with {len(actual)} files")


def validate(root: Path):
    root = root.resolve()
    errors = []
    try:
        manifest = json.loads((root / "CONTENT-MANIFEST.json").read_text(encoding="utf-8"))
        items = manifest["items"]
        if not isinstance(items, list):
            raise TypeError("items must be a list")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"invalid manifest: {exc}"]
    by_id = check_manifest(root, items, errors)
    documents = check_front_matter(root, by_id, errors)
    check_local_links(root, errors)
    check_rtl_structure(root, errors)
    check_registries(root, by_id, documents, errors)
    check_coverage(root, by_id, errors)
    check_inventory(root, errors)
    return errors


if __name__ == "__main__":
    problems = validate(Path(__file__).resolve().parent.parent)
    for problem in problems:
        print(problem)
    print(f"Validation: {len(problems)} error(s)")
    sys.exit(1 if problems else 0)
