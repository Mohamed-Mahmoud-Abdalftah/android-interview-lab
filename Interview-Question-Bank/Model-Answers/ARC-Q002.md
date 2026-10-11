---
id: ARC-Q002-ANSWER
question_id: ARC-Q002
status: reviewed
---
# ARC-Q002 — Complete model answer

**Spoken answer:** “A narrow NoteWriter port keeps the save rule independent of Room and lets a fake verify normalization, no write on invalid input, and failure propagation. It does not prove that the real DAO is durable, transactional, or main-safe.”

<p dir="rtl" lang="ar">الـ use case تحتاج upsert فقط، فتستقبل contract ضيقة. fake تسجل النداء وتثبت ترتيب validation قبل التخزين. لكنها ما تفتحش قاعدة بيانات ولا تختبر process death.</p>

**Mechanics:** Constructor injection gives the caller control over the implementation. NoteWriter is a dependency boundary, while the real adapter must implement its semantic contract and be tested separately. [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data layer guide](https://developer.android.com/topic/architecture/data-layer) were checked 2026-10-10.

**Common wrong answer:** “Because the unit test passes, offline persistence is verified.” A fake has no disk durability.

**Follow-up 1:** Can a concrete class also be injected? Yes. An interface is valuable when it captures a useful contract or substitutions; dependency injection does not require an interface for every class.

**Follow-up 2:** Does using Hilt fix a bad NoteWriter contract? No. Hilt wires a graph; it cannot make an ambiguous or oversized interface semantically sound.

**Rubric for self-review:** Name the behavioral contract, trace validation and storage effects, justify the smallest useful boundary, and separate fake-test proof from Android/database evidence. This is visible practice, not a scored assessment.
