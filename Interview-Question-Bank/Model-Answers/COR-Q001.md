---
id: COR-Q001-ANSWER
question_id: COR-Q001
status: reviewed
---
# COR-Q001 — Complete model answer

**Spoken answer:** “A suspend declaration permits suspension and calling other suspending functions. It does not move blocking work to another thread. I would make the data-layer operation main-safe by moving the blocking call to an appropriate injected dispatcher and test that boundary.”

<p dir="rtl" lang="ar">كلمة suspend تسمح بالتوقف والاستكمال عند suspension point؛ مش بتعمل thread جديد. الـ blocking driver سيظل يحجز main thread إذا نفذ هناك. data layer المالكة للـ driver تختار dispatcher مناسب وتوثق العقد.</p>

**Mechanics:** The caller context supplies the initial execution context. A blocking call runs where called until code explicitly switches context or the API manages its own thread. withContext around the blocking operation can move it; a nonblocking suspending API might need no IO switch. [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html) and [Android coroutine guidance](https://developer.android.com/kotlin/coroutines) were checked 2026-10-10.

**Common wrong answer:** “suspend always runs in the background.” This confuses the language modifier with a scheduling policy.

**Follow-up 1:** What if the driver already exposes a main-safe suspending API? Avoid an automatic extra IO hop; verify its documented contract and test the actual boundary.

**Follow-up 2:** Can runBlocking solve the UI freeze? No. runBlocking blocks the calling thread while it waits, so it is unsuitable for a normal Android main-thread call.

**Rubric for self-review:** State the contract accurately, trace the owner and suspension point, identify the failure or cancellation path, and separate JVM proof from Android integration. This is visible practice, not a scored assessment.
