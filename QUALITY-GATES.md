# Quality gates

## Content status

`planned`: catalog entry only, file may not exist. `draft`: real content but still missing review. `reviewed`: complete lesson/answer/scenario requirements and source checks, with no blank placeholders. Code verification is independent: `not_applicable`, `not_run`, or `tested`. Only observed commands support `tested`. Planned references stay `pending_verification` until a topic-specific official source has been checked. See [manifest](CONTENT-MANIFEST.json).

For a reviewed core lesson, check front matter, outcomes, Egyptian Arabic mental model, exact mechanics and uncertainty, narrated trace, wrong and corrected implementation, alternatives, tests, English explanations, complete follow-ups, visible self-check answers, dated primary sources, and a real path from [START-HERE](START-HERE.md). Use the separate [editorial technical review checklist](EDITORIAL-TECHNICAL-REVIEW.md) to audit technical claims; structural validation alone cannot certify them.

## Arabic and English rendering

Follow the [RTL style guide](RTL-STYLE-GUIDE.md) and [Arabic lesson template](templates/ARABIC-LESSON.md). Arabic headings, prose, lists, and tables need their own `dir="rtl" lang="ar"` elements. Embedded code and English technical fragments need LTR isolation. Keep fenced code, paths, YAML, and English answers in their original LTR source form. Check the [mixed-language fixture](fixtures/RTL-MIXED-LANGUAGE.md) before introducing a new pattern.

The validator detects common missing direction/language attributes, unsafe Markdown syntax inside raw HTML, broken local HTML links and anchors, and invisible bidi controls. A passing structural check does not prove glyph order, punctuation placement, table layout, or copy/paste behavior. Inspect the rendered fixture and a real lesson in VS Code Markdown Preview, Obsidian Reading and Live Preview, and GitHub when those environments are available; record each observed environment separately in [BUILD-VERIFICATION](BUILD-VERIFICATION.md).

## Local validation

Run `python3 -m unittest discover -s scripts -p 'test_*.py' -v` and `python3 scripts/validate.py` from this directory. The validator checks manifest/front matter consistency, IDs, conceptual prerequisites and study sequence, reviewed paths and sections, question/answer relationships and follow-ups, example files, local links and anchors, coverage, inventory, and recorded code-test evidence. It does not judge technical correctness, Arabic fluency, external URL reachability, visual rendering, or educational depth; those require editorial review.

For the JVM lab run `cd projects/kotlin-jvm-labs && ./gradlew clean test check run --no-daemon`. Gradle's JUnit Platform `test` task discovers the Day 1–4, Day 7, Day 13, Day 19, Day 25 and Day 37 tests, and `check` depends on it. Record XML test totals and observed command output in [BUILD-VERIFICATION](BUILD-VERIFICATION.md), not an invented badge.

## Assessment opt-in only

Before any requested assessment, disclose a 100-point rubric: technical correctness 25; causal explanation 20; implementation 20; testing and edge cases 15; trade-offs 10; communication 10. Treat critical misconceptions separately from wording errors, link gaps to a lesson/exercise, and use repeated varied evidence as a readiness guide, never a hiring prediction. No mock is currently active; question-only files and separate answers support future opt-in use.
