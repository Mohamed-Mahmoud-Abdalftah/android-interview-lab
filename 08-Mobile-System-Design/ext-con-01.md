---
id: EXT-CON-01
title: Concurrency
module: 08-Mobile-System-Design
tier: Advanced
estimated_minutes: 90
prerequisite_ids: [COR-006]
learning_outcomes:
  - Explain advanced mechanisms without mixing platform layers
  - Diagnose a realistic failure and defend a trade-off
  - Answer specialist follow-ups with evidence boundaries
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/
  - https://docs.oracle.com/javase/specs/jls/se17/html/jls-17.html
example_paths: []
question_ids: [CON-Q001, CON-Q002, CON-Q003, CON-Q004, CON-Q005, CON-Q006, CON-Q007, CON-Q008, CON-Q009, CON-Q010]
---

# EXT-CON-01 — Concurrency deep interview reference

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Concurrency correctness تبدأ shared state وatomicity وvisibility وordering. Coroutine مش thread، وsingle-thread execution مش ضمان لو callbacks تعيد الدخول أو state مشتركة خارج السياق. اختار immutability أو confinement أو Mutex/atomics حسب invariant، وخلي lock scope صغيرة ومن غير I/O.</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">ارسم الطبقات والـowners بالترتيب، وحدد contract كل boundary والartifact أو state قبلها وبعدها. بعدين أدخل failure في boundary واحدة وتتبع propagation وcleanup وevidence. ما تنقلش guarantee من JVM لـAndroid أو من client لـserver من غير مصدر واختبار مناسب.</p>

### 1. Race definition

<p dir="rtl" lang="ar">A race exists when correctness depends on uncontrolled ordering of conflicting operations.</p>
### 2. Atomicity versus visibility

<p dir="rtl" lang="ar">Visibility exposes writes; atomicity protects an indivisible invariant. One does not automatically provide the other.</p>
### 3. Mutex contract

<p dir="rtl" lang="ar">A coroutine Mutex serializes a critical section but is not reentrant and should not surround slow external work.</p>
### 4. Atomic update

<p dir="rtl" lang="ar">Use a single atomic state/update when the invariant spans fields, not unrelated atomics that can be observed inconsistently.</p>
### 5. Confinement

<p dir="rtl" lang="ar">Owning mutable state on one serialized context can simplify reasoning if every access truly crosses that owner.</p>
### 6. Immutability

<p dir="rtl" lang="ar">Immutable snapshots remove in-place races but publication and stale-version policy still matter.</p>
### 7. Deadlock review

<p dir="rtl" lang="ar">Map lock order and external callbacks; avoid nested locks and calls that can reenter while held.</p>
### 8. Backpressure

<p dir="rtl" lang="ar">Bound queues and define suspend, reject, drop, or conflate policy from event semantics.</p>
### 9. Stress testing

<p dir="rtl" lang="ar">Controlled interleavings prove invariants better than sleeps; stress runs can reveal but not prove absence of races.</p>
### 10. Cancellation and locks

<p dir="rtl" lang="ar">Use structured lock APIs so cancellation releases ownership, and keep cleanup bounded.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar">الحل الغلط هو استخدام الاسم أو abstraction كإجابة نهائية من غير lifetime وfailure وsecurity/evidence. التصحيح يبدأ contract صغيرة، يختبر boundary، ويضيف complexity بس لما requirement أو قياس يبررها.</p>

## Tests and failure cases

- Trace valid, malformed, duplicate, stale, cancellation/restart, and boundary-size cases.
- Use release/device/backend evidence for claims outside pure Kotlin.
- Reject one plausible shortcut and explain the invariant it violates.

## Interview explanation

<p dir="rtl" lang="ar"><strong>الإجابة المختصرة:</strong> A race exists when correctness depends on uncontrolled ordering of conflicting operations.</p>

**English:** “A race exists when correctness depends on uncontrolled ordering of conflicting operations. I would trace the ownership and failure boundaries, compare one viable alternative, and verify the claim with the artifact, test, or production signal that actually observes that layer.”

## Senior follow-ups

1. **What assumption is most dangerous?** counter read-modify-write تضيع updates، أو Mutex ماسكة أثناء network، أو atomic fields منفصلة تكسر invariant مشتركة.
2. **What evidence belongs to this layer?** Use the actual artifact, controlled test, device trace, or backend record; do not infer across layers.
3. **When would you choose a simpler design?** When scale, durability, or isolation requirements do not justify the added operational cost.

## Misconceptions and revision

<p dir="rtl" lang="ar">راجع الأسئلة CON-Q001 إلى CON-Q010. جاوب direct answer ثم mechanism ثم failure ثم test. المحتوى specialist ومش بديل عن vendor/device evidence.</p>
