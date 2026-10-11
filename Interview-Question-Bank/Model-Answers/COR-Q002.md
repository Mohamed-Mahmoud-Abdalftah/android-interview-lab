---
id: COR-Q002-ANSWER
question_id: COR-Q002
status: reviewed
---
# COR-Q002 — Complete model answer

**Spoken answer:** “Both async children start in the same scope. The parent returns after both required values are available; await order only controls where the caller suspends while reading results. It does not impose execution order.”

<p dir="rtl" lang="ar">الـ async اتعملت للاثنين قبل أول await. لو badges خلصت الأول، نتيجتها تستنى جاهزة. الـ parent ما يرجعش card قبل النتيجتين، وcoroutineScope تنتظر أطفالها.</p>

**Mechanics:** The builders create child Deferred values. name.await() may suspend; badges can progress independently. Later badgeCount.await() reads the ready result or suspends until it arrives. The scope completes after children finish. [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html) and [Android coroutine guidance](https://developer.android.com/kotlin/coroutines) were checked 2026-10-10.

**Common wrong answer:** “Because name.await() is first, badges cannot start yet.” Both builders were called before either await.

**Follow-up 1:** What if the second read depends on the first? Use sequential calls or start the dependent work only after the first result; async would add unnecessary concurrency.

**Follow-up 2:** Can the scope return a partial card when a child fails? The example propagates the failure rather than constructing a card with a missing field; an explicit partial-result contract would need a different model.

**Rubric for self-review:** State the contract accurately, trace the owner and suspension point, identify the failure or cancellation path, and separate JVM proof from Android integration. This is visible practice, not a scored assessment.
