---
id: KOT-Q019-ANSWER
question_id: KOT-Q019
status: reviewed
---
# KOT-Q019 — Model answer

**Spoken answer:** “SAM conversion lets Kotlin supply a lambda where a compatible Java single-method interface is expected. It does not define which thread invokes it or how long Java retains it. I inspect registration and unregistration, avoid capturing an Activity unnecessarily, and marshal work to the required owner or thread using the API's documented contract.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـ lambda تختصر كتابة implementation لواجهة Java فيها abstract method واحدة. لكنها ما بتحميش من listener متخزن بعد نهاية الشاشة، ولا تنقل التنفيذ تلقائيًا للـ main thread. لازم أعرف مين مسؤول عن <code dir="ltr">register/unregister</code>، وأمنع singleton يمسك Activity من غير قصد، وأراجع thread اللي الـ Java API بتنادي عليه.</p>

**Mechanics:** [Kotlin Java interoperability](https://kotlinlang.org/docs/java-interop.html) documents SAM conversion; checked 2026-10-10. The Java listener in the question is hypothetical. No Android leak trace or listener integration test exists in this batch, so the exact cleanup API is intentionally unspecified.

**Common wrong answer:** “Kotlin lambda syntax automatically ties the callback to Activity lifecycle.” Lifetime comes from the owner and API registration. **Trade-off:** A short-lived listener can be straightforward; long-lived callbacks need explicit cleanup, weak ownership only where appropriate, and integration tests.

**Follow-up 1:** Could capturing a ViewModel instead of Activity remove every leak risk? **No.** It changes what is retained, but any long-lived registration needs a documented owner and cleanup; the ViewModel also has a lifetime.

**Follow-up 2:** What if Java invokes the callback on a worker thread? **Do not mutate UI state under an assumed main-thread contract.** Confirm the API's thread guarantee and dispatch to the appropriate executor/scope while preserving cancellation and error handling.

**Fair rubric (10):** 2 SAM semantics, 3 lifetime, 3 thread handling, 2 evidence/cleanup plan.
