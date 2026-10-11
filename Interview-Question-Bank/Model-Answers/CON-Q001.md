---
id: CON-Q001-ANSWER
question_id: CON-Q001
status: reviewed
---
# CON-Q001 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A race exists when correctness depends on uncontrolled ordering of conflicting operations.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Two coroutines increment a shared counter using read-modify-write. Write a harmful interleaving and distinguish a race condition from a merely nondeterministic execution order.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Race definition:</strong> الـrace تحصل لما نتيجتين صحيحتين منفردًا تتداخلوا فيكسروا invariant مشتركة. visibility تجعل write مرئية لكنها لا تجعل read-modify-write atomic. الحل يحمي الـtransition كاملة بatomic state أوMutex قصيرة أوserialized owner.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRace definition: اكتب harmful interleaving، اجمع fields في atomic state أو Mutex قصيرة، أو confined owner؛ حدد queue bound/drop policy من معنى الحدث.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Coroutines and visible volatile fields make every compound state transition thread-safe.”

<p dir="rtl" lang="ar">في <strong>Race definition</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Race definition: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Race definition: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Race definition، الـshortcut هي: <bdi dir="ltr">Coroutines and visible volatile fields make every compound state transition thread-safe.</bdi> ودي تكسر: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Race definition: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Race definition: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</span>

## English model answer

“A race exists when correctness depends on uncontrolled ordering of conflicting operations. I would state the shared invariant, demonstrate the harmful interleaving, and choose immutability, confinement, a mutex, or atomic state according to the whole invariant. I would force harmful interleavings, verify atomic state transitions, and cover cancellation while the critical section is active.”
