---
id: COR-Q019-ANSWER
question_id: COR-Q019
status: reviewed
---
# COR-Q019 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “I first ask whether the message must survive recreation and be acknowledged. If it is part of durable UI state, model it with an ID and acknowledgement. A transient effect can use an event stream only when missed delivery is acceptable and ownership is explicit.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A snackbar says Save failed. Should it be StateFlow or SharedFlow?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في State versus event:</strong> StateFlow تحتفظ بقيمة حالية وتعمل equality conflation. SharedFlow تبث للقائمين بالcollection حسب replay وbuffer policy. الاتنين in-memory؛ حدث لازم ينجو من process death أويتنفذ once يحتاج storage وidentity وacknowledgement.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـState versus event: مثّل durable outcome في state أو storage بهوية وacknowledgement، استخدم StateFlow للstate، وSharedFlow فقط للeffects اللي missed delivery فيها مقبولة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “SharedFlow with replay zero is a reliable event bus for payment or navigation results.”

<p dir="rtl" lang="ar">في <strong>State versus event</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في State versus event: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار State versus event: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في State versus event، الـshortcut هي: <bdi dir="ltr">SharedFlow with replay zero is a reliable event bus for payment or navigation results.</bdi> ودي تكسر: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار State versus event: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في State versus event: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</span>

## English model answer

“I first ask whether the message must survive recreation and be acknowledged. If it is part of durable UI state, model it with an ID and acknowledgement. A transient effect can use an event stream only when missed delivery is acceptable and ownership is explicit. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
