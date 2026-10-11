---
id: KOT-Q017-ANSWER
question_id: KOT-Q017
status: reviewed
---
# KOT-Q017 — Model answer

**Spoken answer:** “After current becomes new, fixed returns old because it closes over the separate val snapshot. Live returns new because it reads current when called. Reload-current-profile should read the latest selection at the tap; an event that must retain its original profile should capture a fixed ID.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> <code dir="ltr">snapshot</code> اتاخدت قبل التغيير، فـ <code dir="ltr">fixed</code> شايفاها <code dir="ltr">old</code>. <code dir="ltr">live</code> بتقرأ <code dir="ltr">current</code> وقت النداء، بعد التغيير بقت <code dir="ltr">new</code>. اختيارك يعتمد هل الزر بيقول «أعد تحميل المختار الآن» ولا event تخص عنصر اتحدد في وقت سابق.</p>

**Mechanics:** [Kotlin lambdas](https://kotlinlang.org/docs/lambdas.html) and [local functions](https://kotlinlang.org/docs/functions.html) describe closures over outer values; checked 2026-10-10. The [Day 4 test](../../projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt) checks the current-value path, not a multithreaded race.

**Common wrong answer:** “Closures always snapshot every var.” The explicit snapshot val produces the fixed result here. **Trade-off:** Live reads avoid setup-time staleness but make ownership and concurrent access important; event snapshots preserve original intent.

**Follow-up 1:** Would val live = { current } make current immutable? **No.** Only the live function reference is a val; the captured outer var can still be reassigned and read later.

**Follow-up 2:** Does live guarantee the state cannot change during a network request? **No.** It reads a value for invocation, but request completion and shared-state synchronization require separate policies and tests.

**Fair rubric (10):** 4 exact outputs, 3 contract choice, 2 mutable capture, 1 concurrency limit.
