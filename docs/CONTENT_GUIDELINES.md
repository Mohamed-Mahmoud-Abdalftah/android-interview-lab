# Interview Lab content rules

The bank in `Senior_Android_Interview_Master_Bank.md` owns canonical IDs, English wording, topic, phase, priority, A/B/C group, and order. Run `python3 scripts/import_interview_lab.py` to refresh its manifest and create any missing records. The importer never overwrites an existing record.

Write one distinct explanation in `Interview-Lab/questions/<ID>.md`. Keep its source fields unchanged. A page can move from `source-only` to `reviewed` only after it includes all 14 section headings checked by `scripts/validate_interview_lab.py`, has a relevant primary reference, and a technical review. Record whether review is automated/agent based or external human review; do not conflate them. Use a verified date only on reviewed pages. A question-only route is useful for practice but is not an answer.

Use Egyptian-friendly technical Arabic without translating well-known API names. Keep English short and structured answers speakable. Show imports and assumptions for code. Clearly label conceptual snippets; do not call them tested. Be specific about lifecycle, cancellation, process death, offline behavior, concurrency, and server trust where relevant. Never infer exactly-once network execution from idempotency or treat APK resources as secrets. Check version-sensitive APIs against current official documentation.

Before marking a page reviewed, compare its content to the source question, check related IDs, open cited documents, and verify each citation supports its adjacent claim. Run `python3 scripts/validate_interview_lab.py`; investigate duplicate explanations rather than rewriting only to evade a similarity check. Then rebuild the site and check links.
