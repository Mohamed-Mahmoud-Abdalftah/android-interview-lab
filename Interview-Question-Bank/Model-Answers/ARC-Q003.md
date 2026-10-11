---
id: ARC-Q003-ANSWER
question_id: ARC-Q003
status: reviewed
---
# ARC-Q003 — Complete model answer

**Spoken answer:** “Compilation alone is insufficient. I need the upsert contract to specify outcomes on success and failure, including atomicity or partial effects. I would run shared contract tests against both adapters and document any weaker guarantee.”

<p dir="rtl" lang="ar">الـ interface تقول شكل method فقط. لو implementation تخزن ثم ترمي، caller ممكن يعيد الطلب ويعمل duplicate أو يعرض فشل رغم التخزين. لازم توضيح transaction وidempotency.</p>

**Mechanics:** Behavioral substitution includes preconditions, postconditions, failure semantics and observable side effects. The JVM fake verifies delegation, while real adapters need contract and integration tests. [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data layer guide](https://developer.android.com/topic/architecture/data-layer) were checked 2026-10-10.

**Common wrong answer:** “Both implement NoteWriter, therefore LSP is satisfied.” Type conformance is narrower than behavioral substitutability.

**Follow-up 1:** Could the use case catch and retry every exception? No. A retry after partial write may duplicate side effects unless the adapter guarantees idempotency or transactions.

**Follow-up 2:** What if one backend cannot meet atomic upsert? Expose the weaker outcome explicitly, revise the port or choose a compensating workflow; do not promise a guarantee the adapter cannot supply.

**Rubric for self-review:** Name the behavioral contract, trace validation and storage effects, justify the smallest useful boundary, and separate fake-test proof from Android/database evidence. This is visible practice, not a scored assessment.
