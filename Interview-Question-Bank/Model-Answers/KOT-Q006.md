---
id: KOT-Q006-ANSWER
question_id: KOT-Q006
status: reviewed
---
# KOT-Q006 — Model answer

**Spoken answer:** “`val` prevents me from assigning a different list to `labels`; it does not freeze the list object. `labels.add("Mona")` is allowed, and `alias` sees the same list with two elements. A `var` would also allow rebinding `labels`, but that would not change the old object held by `alias`. For a stable value I would create a copy at the boundary.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> <code dir="ltr">val</code> بيثبّت الربط بين الاسم والـ object، لكن <code dir="ltr">mutableListOf</code> لسه قابلة للتعديل. بعد <code dir="ltr">add("Mona")</code>، <code dir="ltr">alias</code> بتشوف نفس الـ list المعدّلة. لو الربط <code dir="ltr">var</code>، تقدر تشير بـ <code dir="ltr">labels</code> لقائمة تانية، لكن <code dir="ltr">alias</code> تفضل ماسكة القديمة. ده فرق بين تغيير المرجع وتغيير محتوى الكائن.</p>

**Mechanics:** Kotlin's `val` local can be assigned only once; `var` can be reassigned. `MutableList` exposes writes even through a `val` binding. Two references to the same list observe the same in-place mutations. A `List<String>` parameter limits writes through that Kotlin type, but it does not freeze an object reachable through another alias. [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html) and [collections overview](https://kotlinlang.org/docs/collections-overview.html), checked 2026-10-10.

**Common wrong answer:** “`val` makes everything recursively immutable.” It constrains one binding. **When not to copy:** If the API explicitly promises a live view and all owners coordinate changes, a snapshot would change the contract; document and test that decision.

**Follow-up 1:** Would `val view: List<String> = labels` make `alias` unable to mutate? **No.** The read-only type blocks `view.add`, but `alias` and `labels` still hold the mutable object. A caller needing a stable snapshot needs a separate list of elements.

**Follow-up 2:** If `labels` were a `var` and reassigned to a new list, what would `alias` see? **It would still refer to the original list.** Reassignment changes only that binding; it does not retarget other references or mutate the old object.

**Fair rubric (10):** 3 binding/object distinction, 2 alias trace, 2 `var` rebind effect, 2 boundary design, 1 live-view caveat. No Android runtime claim.
