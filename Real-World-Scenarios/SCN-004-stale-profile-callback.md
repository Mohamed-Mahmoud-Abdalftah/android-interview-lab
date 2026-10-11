---
id: SCN-004
lesson_id: KOT-004
status: reviewed
code_verification: tested
---
# SCN-004 — Reload targets the previous profile

**Hypothetical incident.** A profile screen creates a reload action while profile A is selected. The user switches to B and taps Reload, but the request uses A. This is a timing and ownership exercise, not a reported production event. Start with [KOT-004](../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md).

<p dir="rtl" lang="ar">أول فرضية إن callback حفظت <code dir="ltr">idAtSetup</code> وقت إنشاء الزر. لا نعلن root cause من الشكوى وحدها: سجل event sequence بعد إخفاء المعرّفات الحساسة، وتأكد من ID عند إنشاء callback وعند الضغط وعند إرسال الطلب. فرضية تانية إن الطلب صح لكن response قديمة وصلت متأخر؛ دي مشكلة مختلفة.</p>

## Reproduction and competing causes

1. Select A, create the callback, switch to B, invoke it. If the sent argument remains A, inspect where the ID was captured.
2. If the sent argument is B but A appears on screen, record request generations and completion order. The callback fix alone cannot order asynchronous responses.
3. If no request is sent, inspect null/blank state, owner lifetime, and whether the callback was unregistered.

The [JVM lab](../Coding-Challenges/LAB-004-deferred-profile-request.md) exercises the first and third branches synchronously. It does not execute Android lifecycle or network responses.

## Correction and rollout

<p dir="rtl" lang="ar">لعقد "Reload أحدث اختيار" اقرأ provider مرة وقت الضغط، تحقق من ID ثم مرره للطلب. لعقد "أعد إرسال الحدث الأصلي" احتفظ بـ snapshot مقصودة. وثّق الفرق في API. لو عندك async response، اربط النتيجة بـ request generation أو cancellation حسب احتياج الشاشة. لا تعتبر قراءة ID الحالية ضمانة لكل أنواع stale data.</p>

Add the A-to-B transition test, a blank-state test, and a thrown-request test. In an Android implementation, separately test owner disposal and late response handling. During rollout, observe the exact wrong-profile signature with redacted telemetry and revert the callback change if it produces incorrect event semantics. No rollout or measured incident rate has occurred here.

## Senior follow-ups

1. **Why not always capture a snapshot?** An event-time value is correct for an immutable event, but wrong when the action promises the current selection.
2. **Does reading current state make the request thread-safe?** No. The provider contract and caller thread still need an owner and synchronization policy.
