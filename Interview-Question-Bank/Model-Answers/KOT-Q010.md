---
id: KOT-Q010-ANSWER
question_id: KOT-Q010
status: reviewed
---
# KOT-Q010 — Model answer

**Spoken answer:** “`val` prevents rebinding one Kotlin reference, and `List<String>` prevents mutation through that Kotlin interface. Neither stops the Java SDK from changing the live backing list. If callers need a stable list of strings, I copy the elements into a separately owned list at the boundary and expose a read-only type. The copy is shallow, and I must coordinate with the SDK if it can mutate during the copy.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> الـ <code dir="ltr">val</code> مش بيجمّد الـ object، و<code dir="ltr">List&lt;String&gt;</code> بتمنع الكتابة من المرجع ده في Kotlin بس. لو Java SDK لسه ماسكة نفس الـ list وعدّلتها، اللي بيقرأوا الـ property ممكن يشوفوا التغيير. لو العقد المطلوب <code dir="ltr">snapshot</code>، انسخ العناصر في list مملوكة للتطبيق عند الـ boundary. النسخة سطحية؛ ولو Java بتعدّل في نفس لحظة النسخ، لازم تنسّق القراءة حسب عقد الـ SDK.</p>

**Mechanics:** Kotlin maps Java collection types to Kotlin collection views at compile time; the runtime object remains the same. A read-only Kotlin `List` interface is not an immutable-object guarantee. For a stable structural snapshot of strings, make a new list from the returned elements and avoid retaining the mutable SDK list. If elements themselves are mutable, copying only the container does not freeze them. [Kotlin Java interop](https://kotlinlang.org/docs/java-interop.html) and [collections overview](https://kotlinlang.org/docs/collections-overview.html), checked 2026-10-10.

**Common wrong answer:** “`val` plus `List` guarantees thread safety.” Neither declaration coordinates concurrent SDK writes. **When not to snapshot:** If a live collection is the intended contract, expose that fact through an explicit owner or update stream and define synchronization instead of pretending it is stable.

**Follow-up 1:** Is a Java `Collections.unmodifiableList(live)` wrapper a snapshot? **No.** It blocks mutations through that wrapper, but changes through the SDK's original reference remain visible. A separately owned copy is needed for point-in-time list contents.

**Follow-up 2:** What if the SDK updates the list while Kotlin is copying it? **A copy alone gives no atomic snapshot guarantee.** Use the SDK's documented locking/callback ownership rules, or request a snapshot API, and test the relevant race. Also validate nullability separately if the Java method is unannotated; this prompt assumed a non-null result.

**Fair rubric (10):** 2 `val` binding, 2 read-only interface, 2 aliasing, 2 snapshot design, 2 shallow-copy/concurrency limits. No claim that every Java SDK returns a mutable list.
