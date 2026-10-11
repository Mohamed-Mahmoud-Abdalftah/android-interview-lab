---
id: KOT-Q018-ANSWER
question_id: KOT-Q018
status: reviewed
---
# KOT-Q018 — Model answer

**Spoken answer:** “The setup code saved an ID before the click, so the callback later sends a stale value. If the button means reload the current selection, I pass a provider and read one validated ID at invocation. The local Boolean means a request callback was invoked, not that remote work succeeded or the response is still relevant.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـ bug حصل لأن <code dir="ltr">idAtSetup</code> اتثبت وقت إنشاء الزر. المستخدم غيّر الاختيار، لكن الـ lambda لسه ماسكة ID القديم. الحل تقرأ provider وقت الضغط، تنظف القيمة، وتستدعي request لو صالحة. لو الـ request ترمي exception، ما تحولهاش بصمت لـ false. ولو الشبكة async، نتيجة true مش معناها تحميل ناجح.</p>

**Mechanics:** The [runnable callback](../../projects/kotlin-jvm-labs/src/main/kotlin/academy/DeferredRequest.kt) and [JUnit tests](../../projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt) check invocation timing, blank suppression and exception propagation. [Kotlin functions](https://kotlinlang.org/docs/functions.html) and [lambdas](https://kotlinlang.org/docs/lambdas.html) were checked 2026-10-10.

**Common wrong answer:** “Read current state once when the ViewModel starts, because the callback executes later.” That repeats the stale snapshot. **Trade-off:** Reading current state at tap time is wrong for an event whose identity must remain fixed; use a deliberate event snapshot then.

**Follow-up 1:** What if an older request completes after a newer one? **This callback design alone cannot reject the old result.** Give requests an owner/generation or cancellation policy and test reordering in the coroutine module.

**Follow-up 2:** What if the provider returns spaces or null? **Do not call request.** The local function returns false to mean no delegation occurred, which the Day 4 negative tests verify.

**Fair rubric (10):** 3 cause, 3 corrected timing, 2 Boolean meaning, 2 stale-response limit.
