---
id: KOT-Q014-ANSWER
question_id: KOT-Q014
status: reviewed
---
# KOT-Q014 — Model answer

**Spoken answer:** “Base initialization runs before derived property initialization. A call to an open member in the base init block can dispatch to the derived override, which may read state that is not ready. I would locate the call in the construction trace, move initialization work into final logic using constructor arguments, and invoke overridable behavior only after construction.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـ base بتبدأ قبل ما fields بتاعة derived تتجهز. لو الـ base نادت method <code dir="ltr">open</code>، الـ dispatch يقدر يدخل override في derived بدري. ساعتها قراءة field متأخرة ممكن تفشل أو تعطي قيمة غير متوقعة. افحص ترتيب الـ constructors والـ stack trace، واعزل الـ initialization في دوال مش قابلة للـ override أو استخدم input صريح.</p>

**Mechanics:** The [Kotlin inheritance guide](https://kotlinlang.org/docs/inheritance.html) explicitly warns against open-member use in constructors, property initializers, and init blocks; checked 2026-10-10. A minimal reproducer should log the order and test a safe redesign. The specific exception type can depend on the code, compiler and target, so the contract-level diagnosis is the premature dispatch.

**Common wrong answer:** “The override cannot run before derived init because Kotlin is null-safe.” Nullability does not alter virtual dispatch or construction order. **Trade-off:** Keep extension points for post-construction behavior; avoid turning every base method final if a legitimate override is needed later.

**Follow-up 1:** Is reading a final base constructor parameter from base init safe? **Yes, when the argument evaluation has completed and the base owns that value.** Do not call an open getter that reads derived state indirectly.

**Follow-up 2:** What evidence separates this from a missing Java value? **The stack trace should show the base initialization call entering a derived override during construction.** A controlled constructor-order trace and a test after moving the call establish whether order caused the failure.

**Fair rubric (10):** 4 order and dispatch, 2 evidence, 2 redesign, 2 boundary against null-safety myths.
