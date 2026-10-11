---
id: ARC-Q004-ANSWER
question_id: ARC-Q004
status: reviewed
---
# ARC-Q004 — Complete model answer

**Spoken answer:** “The use case needs only upsert, so a narrow port makes its dependency and test surface clear. I would split only when the wider interface creates coupling or competing implementers; extra interfaces without a use can raise navigation cost.”

<p dir="rtl" lang="ar">الـ use case للكتابة لا تحتاج read أو sync، فواجهة صغيرة تكفي. لكن لو كل العمليات متلازمة في feature بسيطة، تقسيمها لعشرات interfaces ممكن يزيد تعقيد بلا فائدة.</p>

**Mechanics:** Interface segregation is about clients depending only on operations they use. In Kotlin the fun interface makes a one-method test fake concise, but syntax alone does not justify the abstraction. [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data layer guide](https://developer.android.com/topic/architecture/data-layer) were checked 2026-10-10.

**Common wrong answer:** “More interfaces always mean better SOLID.” An interface must express a meaningful client contract.

**Follow-up 1:** What if a second use case reads notes? Define the read contract it needs, or use a cohesive repository if the wider API remains stable and understandable.

**Follow-up 2:** Is a fake implementation enough to validate interface design? No. A real adapter and actual change pressure reveal whether the boundary is convenient and semantically accurate.

**Rubric for self-review:** Name the behavioral contract, trace validation and storage effects, justify the smallest useful boundary, and separate fake-test proof from Android/database evidence. This is visible practice, not a scored assessment.
