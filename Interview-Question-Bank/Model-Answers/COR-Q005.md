---
id: COR-Q005-ANSWER
question_id: COR-Q005
status: reviewed
---
# COR-Q005 — Complete model answer

**Spoken answer:** “launch gives a Job for work without a direct value; async gives a Deferred result; withContext runs a block in a chosen context and returns its result; runBlocking bridges synchronous callers by blocking their thread. A structured caller should await or join as appropriate and let failures reach a known owner.”

<p dir="rtl" lang="ar">اختيار builder حسب result والمالك. في المعمل async ترجع اسم وعدد badges؛ await توصل result أو failure. withContext تنقل block. runBlocking محجوزة للـ boundary المتزامنة أو اختبار مناسب، مش UI main.</p>

**Mechanics:** Both async children belong to coroutineScope, so failure of a normal child cancels the scope and siblings. The exact exception observation can depend on builder and parent context; an owner must handle it intentionally rather than launch and forget. [Kotlin coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html) and [Android coroutine guidance](https://developer.android.com/kotlin/coroutines) were checked 2026-10-10.

**Common wrong answer:** “async automatically swallows errors until someone chooses to check.” In a structured scope, child failure can cancel the parent; silently ignoring a Deferred is unsafe.

**Follow-up 1:** When is launch preferable here? For a caller-owned action with no returned value, such as initiating a UI event handler, provided its Job and failure are owned by the scope.

**Follow-up 2:** What if one source may fail without cancelling the other? That is a different error-isolation contract. Model partial results or supervision explicitly, and test that policy instead of silently catching every exception.

**Rubric for self-review:** State the contract accurately, trace the owner and suspension point, identify the failure or cancellation path, and separate JVM proof from Android integration. This is visible practice, not a scored assessment.
