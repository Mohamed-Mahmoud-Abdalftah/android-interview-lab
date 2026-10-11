---
id: COR-Q006-ANSWER
question_id: COR-Q006
status: reviewed
---
# COR-Q006 — Complete model answer

**Spoken answer:** “Inside a regular coroutineScope, the IOException is a child failure. It fails the parent and the parent cancels the suspended siblings. The scope completes exceptionally after child cleanup. Returning partial data requires an explicit different contract, usually supervision plus a typed result for each child.”

<p dir="rtl" lang="ar">ارسم الشجرة قبل ما تقول النتيجة: الثلاثة أولاد لنفس scope. فشل الثاني مش isolated؛ يصعد للـparent، والـparent يلغي الأول والثالث. الـcaller ما يستلمش list ناقصة. لو الـproduct يسمح partial data، غيّر العقد بوضوح إلى supervisor وخلّي كل child ترجع success أو failure معروفة، من غير ما تحول cancellation لبيانات.</p>

**Mechanics:** `coroutineScope` waits for all children, including their cancellation cleanup. A non-cancellation child exception cancels its parent, which cancels sibling children. `supervisorScope` changes sibling-failure propagation, not parent cancellation. The contract is documented in the Kotlin exception handling and supervisorScope references checked 2026-10-11.

**Common wrong answer:** “Only the failed Deferred stops because exceptions stay inside async.” The Deferred stores the exception for `await`, but structured parent-child failure rules still apply.

**Follow-up 1:** What if a sibling is in `finally`? The parent waits for its cleanup; keep cleanup bounded and use `NonCancellable` only for a small operation that truly must finish.

**Follow-up 2:** Should the UI show two cards and silently omit one? No. Partial success must be visible in the state model so loading, error, stale, and success states cannot be confused.

**Rubric for self-review:** Name parent and children, trace failure and cancellation separately, state the product contract, and mention cleanup timing.
