---
id: COR-Q009-ANSWER
question_id: COR-Q009
status: reviewed
---
# COR-Q009 — Complete model answer

**Spoken answer:** “`runCatching` catches `Throwable`, including CancellationException. If I convert that to a normal failure, cancelled work may continue and publish stale state. I rethrow cancellation, or call `ensureActive` before mapping expected failures, and I catch only exceptions the boundary can classify.”

<p dir="rtl" lang="ar">الإلغاء control flow متعلق بعمر العملية، مش network error. لما الشاشة أو worker owner تلغي، لازم suspension ترجع الإشارة لفوق بسرعة. بلعها ممكن يكمل retry أو database write بعد انتهاء المالك. التصحيح يمسك IOException مثلًا، ويرمي CancellationException فورًا.</p>

**Mechanics:** Coroutine cancellation is cooperative and is represented by `CancellationException` at suspending checkpoints. A broad `Throwable` catch intercepts it. Cleanup belongs in `finally`; business error mapping must preserve the cancelled state.

**Common wrong answer:** “CancellationException is harmless because coroutines ignore it.” The machinery treats it specially only if code lets it propagate.

**Follow-up 1:** Is catching `Exception` safe? No. `CancellationException` is an exception, so it is still caught.

**Follow-up 2:** What should a test assert? Start a suspended operation, cancel its parent, await it, and assert cancellation is observable and no success/error state is published afterward.

**Rubric for self-review:** State why the bug survives code review, show the corrected catch order, and give a deterministic cancellation test.
