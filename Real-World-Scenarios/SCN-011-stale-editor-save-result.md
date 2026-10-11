---
id: SCN-011
lesson_id: ARC-002
status: reviewed
code_verification: not_run
---
# SCN-011 — Old save response reports success for a new title

**Hypothetical investigation.** An editor starts saving title A. The user changes it to B and saves again. A's response arrives after B began, and the screen displays “Saved” even though B is pending. No production trace or Android device run exists. Start with [ARC-002](../04-Architecture-DI/arc-002-mvvm-udf-state-and-events.md).

<p dir="rtl" lang="ar">سجل timeline بأرقام طلبات واضحة: draft عند بداية كل operation، وقت dispatch، completion، state قبل وبعد الرد، والـ record المكتوب فعليًا. افصل عرض success الغلط عن احتمال overwrite في التخزين؛ الاتنين ممكن يحصلوا من أسباب مختلفة. فرضيات: callback بدون identity، قراءة draft متغيرة أثناء الكتابة، أو collector قديم يكتب في view جديدة.</p>

## Reproduction and competing causes

1. Start request 1 for A; edit title to B; start request 2; deliver success for request 1. The [pure reducer test](../projects/kotlin-jvm-labs/src/test/kotlin/academy/EditorReducerTest.kt) requires no visible success for B.
2. Deliver request 2 success, then request 1 failure. Confirm old failure cannot replace current success.
3. Use a recording repository to inspect the title snapshot passed at each start. A UI guard alone cannot establish what persisted.
4. Recreate the view while requests are pending and verify collection/ownership with an Android lifecycle test when an SDK is available.

## Correction and evidence limit

<p dir="rtl" lang="ar">اربط completion بهوية الطلب الحالي؛ لو الرد قديم تجاهله في UI. لو product يسمح بطلب حفظ واحد فقط، امنع الطلب التاني أو اعمل queue بوضوح. لو يسمح بالتوازي، حدد ترتيب الكتابة، version conflict، وsource of truth. راقب mismatch بين title المعروض والبيانات المقروءة من repository بعد refresh؛ لا تعتبر الرسالة دليل durability.</p>

The JVM test proves the reducer's stale response behavior only. A repository integration test, Android lifecycle test, and device observation remain necessary. No rollout or incident rate is claimed.

## Senior follow-ups

1. **Does cancellation guarantee no write?** No. The downstream operation may already have committed; reconcile against the repository.
2. **What if request identities wrap?** Use an identity scheme appropriate to the lifetime and concurrency of real requests; this lab's Int is educational.
