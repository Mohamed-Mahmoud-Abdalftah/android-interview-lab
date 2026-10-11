---
id: KOT-Q007-ANSWER
question_id: KOT-Q007
status: reviewed
---
# KOT-Q007 — Model answer

**Spoken answer:** “The initializer gives `inferred` the static type `MutableList<String>`, so `inferred.add` compiles. The declared type of `view` is `List<String>`, which has no `add`, so `view.add` does not compile. Both names still refer to the same underlying list, so `view` is not a snapshot. I use an explicit type at a public boundary to state the intended operations, and copy when I promise stable contents.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> الـ compiler استنتج <code dir="ltr">MutableList&lt;String&gt;</code> لـ <code dir="ltr">inferred</code> من <code dir="ltr">mutableListOf("Ada")</code>. أما <code dir="ltr">view</code> فنوعها المعلن <code dir="ltr">List&lt;String&gt;</code>، فـ <code dir="ltr">view.add("Mona")</code> مش متاحة وقت الـ compile. الاتنين بيشيروا لنفس القائمة؛ لو <code dir="ltr">inferred</code> اتعدّلت، القراية من <code dir="ltr">view</code> هتشوف التغيير. النوع المعلن بيحدّد العمليات المتاحة، مش نسخة مستقلة من البيانات.</p>

**Mechanics:** Type inference fixes a static type from the initializer; it does not turn the variable into a dynamically changing type. `List` is the read-only interface and `MutableList` adds write operations. Declaring `List<String>` at an API edge communicates a narrower Kotlin contract, but a mutable alias can still change the backing object. [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html), [properties](https://kotlinlang.org/docs/properties.html), and [collections overview](https://kotlinlang.org/docs/collections-overview.html), checked 2026-10-10.

**Common wrong answer:** “An explicit `List` type copied the list.” It only changed the static view. **When not to force an explicit local type:** A short local initializer can be clearer with inference if no boundary contract is involved.

**Follow-up 1:** Why declare `List<String>` on a return type if it is not deeply immutable? **It prevents ordinary Kotlin callers from calling mutators through that reference and keeps the public API narrow.** If callers also need a stable point-in-time value, the implementation must copy and define element immutability separately.

**Follow-up 2:** Does `val count = 1` later become a `String` if you assign text? **No.** The inferred type is `Int`, and `val` cannot be reassigned at all. With a `var`, reassignment still has to respect its declared or inferred type.

**Fair rubric (10):** 3 static types, 2 compile outcomes, 2 alias/snapshot distinction, 2 API-boundary reason, 1 inference caveat. No Android dependency.
