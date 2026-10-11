---
id: COR-Q017-ANSWER
question_id: COR-Q017
status: reviewed
---
# COR-Q017 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “StateFlow uses equality-based conflation. If the new value compares equal to the current value, collectors are not notified. State should be immutable and equality must represent every observable field.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Why might assigning an equal data-class value to MutableStateFlow produce no new emission?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في StateFlow conflation:</strong> StateFlow تحتفظ بقيمة حالية وتعمل equality conflation. SharedFlow تبث للقائمين بالcollection حسب replay وbuffer policy. الاتنين in-memory؛ حدث لازم ينجو من process death أويتنفذ once يحتاج storage وidentity وacknowledgement.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـStateFlow conflation: مثّل durable outcome في state أو storage بهوية وacknowledgement، استخدم StateFlow للstate، وSharedFlow فقط للeffects اللي missed delivery فيها مقبولة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “SharedFlow with replay zero is a reliable event bus for payment or navigation results.”

<p dir="rtl" lang="ar">في <strong>StateFlow conflation</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في StateFlow conflation: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار StateFlow conflation: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في StateFlow conflation، الـshortcut هي: <bdi dir="ltr">SharedFlow with replay zero is a reliable event bus for payment or navigation results.</bdi> ودي تكسر: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار StateFlow conflation: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في StateFlow conflation: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</span>

## English model answer

“StateFlow uses equality-based conflation. If the new value compares equal to the current value, collectors are not notified. State should be immutable and equality must represent every observable field. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
