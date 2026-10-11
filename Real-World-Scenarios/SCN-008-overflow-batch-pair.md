---
id: SCN-008
lesson_id: SYS-001
status: reviewed
code_verification: tested
---
# SCN-008 — A false pair at the Int boundary

**Hypothetical incident.** An offline batch planner selects two chunk sizes whose sum is supposed to equal a target. With extreme values, it reports a pair that cannot meet the target mathematically. No production app, dataset, crash rate or device is observed here. Start with [SYS-001](../08-Mobile-System-Design/sys-001-arrays-maps-two-pointers-and-invariants.md).

<p dir="rtl" lang="ar">الفرضية الأساسية overflow في <code dir="ltr">Int</code>: <code dir="ltr">Int.MAX_VALUE + 1</code> تلتف في JVM إلى <code dir="ltr">Int.MIN_VALUE</code>. لكن راجع العقد أولًا: هل sizes فعلًا Int؟ هل target مقصود كـ bytes؟ هل فيه negative sentinel؟ لا تغير algorithm قبل تثبيت input وexpected result.</p>

## Reproduction and competing causes

1. Reproduce with `[Int.MAX_VALUE, 1]` and target `Int.MIN_VALUE`. A false match supports overflow; the corrected [JVM test](../projects/kotlin-jvm-labs/src/test/kotlin/academy/PairSearchTest.kt) expects no pair.
2. Check whether an in-place sort changed original indices. If selected positions now refer to another chunk, that is a separate contract violation.
3. Check whether duplicate values were mistaken for a single element used twice. A one-element array can never produce a two-index pair.
4. Inspect whether an upstream unit conversion truncated a Long byte count before it reached the algorithm.

## Correction and verification

<p dir="rtl" lang="ar">احسب complement والمجموع بـ <code dir="ltr">Long</code> قبل مقارنة target، وارفض complement خارج مدى Int. احفظ original indices، وابحث في map قبل إدخال current. اختبر extreme values وduplicates وعدم تغيير input. لو product تحتاج أحجام أكبر من Int أصلًا، غيّر model إلى Long بدل ترقيع algorithm عند آخر لحظة.</p>

The [challenge](../Coding-Challenges/LAB-008-pair-search-invariants.md) and pure JVM tests execute these branches. They do not validate real chunk metadata or Android storage. Rollout would compare old/new planner results on a redacted sample, verify size units and rollback on mismatch; no rollout or measurement is claimed.

## Senior follow-ups

1. **Does Long intermediate arithmetic make an Int domain big enough?** No. If legitimate sizes exceed Int, input/model types need revision.
2. **Is a hash-map lookup always O(1)?** Only under suitable hashing assumptions; cite the implementation contract and measure the real workload if performance matters.
