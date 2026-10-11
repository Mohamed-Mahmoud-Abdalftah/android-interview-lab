---
id: KOT-Q003-ANSWER
question_id: KOT-Q003
status: reviewed
---
# KOT-Q003 — Model answer

**Spoken answer:** “The two property accesses can observe different values, so Kotlin may refuse the smart cast. I capture `val snapshot = holder.name` and check that local before using it. This keeps the two operations on one value, but it does not make updates to the holder atomic.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> <code dir="ltr">holder.name</code> اتقرت مرتين في المثال؛ ممكن الـ getter أو state ترجع قيمة مختلفة. خزّن أول قراءة في <code dir="ltr">val snapshot</code> وافحص نفس القيمة اللي هتستخدمها. ده لا يحوّل تحديثات الـ holder إلى عملية atomic.</p>

**Mechanics:** Smart casts require stability the compiler can prove. A mutable/open property may change between the check and use. `val snapshot = holder.name; if (snapshot != null) println(snapshot.length)` is the safe local pattern. For shared mutable state, use an appropriate synchronization or ownership model as well. [Kotlin type checks and casts](https://kotlinlang.org/docs/typecasts.html), checked 2026-10-10.

**Common wrong answer:** “`val` always means immutable state.” A `val` reference can point to mutable data; here it means this local reference is not reassigned. **When not to use a snapshot alone:** If business logic needs a consistent multi-field state, capture or synchronize the whole state transition.

**Follow-up 1:** Can a `val` custom getter be smart cast automatically? **Not generally.** A getter may return a different value on the next call; use a local.

**Follow-up 2:** Does `snapshot` prevent another thread changing `holder.name`? **No.** It preserves the old reference for this computation; it does not freeze the owner.

**Fair rubric (10):** 3 repeated-read risk, 3 correct local pattern, 2 concurrency distinction, 2 follow-up reasoning. Version caveat: precise smart-cast cases can evolve; rely on documented compiler stability rules.
