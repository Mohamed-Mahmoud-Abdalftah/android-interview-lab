---
id: COR-Q004-ANSWER
question_id: COR-Q004
status: reviewed
---
# COR-Q004 — Complete model answer

**Spoken answer:** “Injection lets production select an appropriate execution context and lets tests control scheduling. A StandardTestDispatcher test can verify completion and cancellation deterministically; it does not prove Android lifecycle, thread performance, or real I/O behavior.”

<p dir="rtl" lang="ar">حقن dispatcher بيفصل قرار التنفيذ عن منطق جمع النتيجة، وبيسمح للاختبار يشغّل work الجاهز بجدولته. لكن نجاح الاختبار لا يقيس سرعة ولا يثبت سلوك جهاز.</p>

**Mechanics:** withContext uses the injected dispatcher for the block while retaining the caller Job in its context. The tests use one testScheduler, runCurrent, and CompletableDeferred gates to check state before and after completing each source. [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html) and [Android coroutine guidance](https://developer.android.com/kotlin/coroutines) were checked 2026-10-10.

**Common wrong answer:** “A test dispatcher makes the code thread-safe.” It only controls scheduling in the test; shared state and external APIs still need their own contracts.

**Follow-up 1:** When might you skip a dispatcher switch? When the called suspend API is already documented as main-safe and the extra hop adds no useful boundary.

**Follow-up 2:** Can a test scheduler simulate every race? No. It is excellent for deterministic logical paths, while integration and stress tests may still be needed for thread and lifecycle interactions.

**Rubric for self-review:** State the contract accurately, trace the owner and suspension point, identify the failure or cancellation path, and separate JVM proof from Android integration. This is visible practice, not a scored assessment.
