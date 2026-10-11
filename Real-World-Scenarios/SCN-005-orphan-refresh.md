---
id: SCN-005
lesson_id: COR-001
status: reviewed
code_verification: not_run
---
# SCN-005 — Refresh survives its screen

**Hypothetical incident, not an observed crash.** A profile refresh begins, the user leaves the screen, and a late callback tries to publish an old result. The available evidence is only this symptom; device, lifecycle owner, transport, stack trace and frequency are unknown. Start with [COR-001](../02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md).

<p dir="rtl" lang="ar">احتمال أول إن الشغل اتطلق في <code dir="ltr">GlobalScope</code> أو scope عمرها أطول من الشاشة. احتمال تاني إن scope صح لكن مصدر الشبكة لا يتعاون مع cancellation أو نتيجة request قديمة نشرت بعد اختيار جديد. لازم نفرّق بين Job اتلغت والطلب الفعلي توقف، وبين طلب جديد وresponse قديمة.</p>

## Evidence to collect

1. Record redacted timestamps for navigation, refresh start, cancellation request, transport completion and state publication. Never log full profile identifiers or tokens.
2. Reproduce with a controlled fake source that waits on a gate. Destroy the intended owner before releasing the gate; observe whether the child is cancelled and whether state publication is suppressed.
3. Compare owner lifetimes: Fragment view, Fragment, ViewModel and application scope are different contracts. A ViewModel can survive a view recreation, so scope choice depends on desired lifetime.
4. Inspect whether the transport is genuinely cancellable and whether a generation or selection check is needed for out-of-order responses.

## Correction and tests

<p dir="rtl" lang="ar">انقل launch إلى owner مناسب، وخلي child request تحت parent واضح. لو النتيجة مرتبطة باختيار معيّن، خزّن generation أو ID عند الطلب وافحصها وقت النشر. عالج إلغاء transport في adapter لو الـ API تدعم ده، واكتب اختبارين منفصلين: واحد لإلغاء parent وواحد لنتيجة قديمة بعد طلب أحدث.</p>

The [JVM challenge](../Coding-Challenges/LAB-005-profile-card-scope.md) proves structured cancellation of two waiting children, not navigation or a real transport. Android lifecycle and fake-network integration tests remain necessary. A broad exception catch, arbitrary delay, or detached GlobalScope launch would mask the ownership bug.

**Rollout plan, unexecuted:** Land the fake reproducer, change one owner boundary, verify against supported navigation paths and screen rotation, then monitor the exact late-update signature in a staged release. No rollout or metric is claimed here.

## Senior follow-ups

1. **Is viewModelScope always the right owner?** No. It is appropriate for ViewModel work, while a view-only collector may require a narrower lifecycle.
2. **Does cancelled Job mean the server never processed the request?** No. Cancellation propagation and remote side effects are different; make request idempotency and result ownership explicit.
