---
id: CON-Q003-ANSWER
question_id: CON-Q003
status: reviewed
---
# CON-Q003 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A coroutine Mutex serializes a critical section but is not reentrant and should not surround slow external work.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A coroutine Mutex protects a map, but the critical section performs network I/O and calls user code. Review cancellation, reentrancy, latency, and the invariant that should actually be locked.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Mutex contract:</strong> الـrace تحصل لما نتيجتين صحيحتين منفردًا تتداخلوا فيكسروا invariant مشتركة. visibility تجعل write مرئية لكنها لا تجعل read-modify-write atomic. الحل يحمي الـtransition كاملة بatomic state أوMutex قصيرة أوserialized owner.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMutex contract: اكتب harmful interleaving، اجمع fields في atomic state أو Mutex قصيرة، أو confined owner؛ حدد queue bound/drop policy من معنى الحدث.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Coroutines and visible volatile fields make every compound state transition thread-safe.”

<p dir="rtl" lang="ar">في <strong>Mutex contract</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Mutex contract: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Mutex contract: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Mutex contract، الـshortcut هي: <bdi dir="ltr">Coroutines and visible volatile fields make every compound state transition thread-safe.</bdi> ودي تكسر: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Mutex contract: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Mutex contract: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</span>

## English model answer

“A coroutine Mutex serializes a critical section but is not reentrant and should not surround slow external work. I would state the shared invariant, demonstrate the harmful interleaving, and choose immutability, confinement, a mutex, or atomic state according to the whole invariant. I would force harmful interleavings, verify atomic state transitions, and cover cancellation while the critical section is active.”
