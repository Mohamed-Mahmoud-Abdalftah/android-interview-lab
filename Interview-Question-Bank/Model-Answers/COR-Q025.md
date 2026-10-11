---
id: COR-Q025-ANSWER
question_id: COR-Q025
status: reviewed
---
# COR-Q025 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “I classify each value: durable business event, diagnostic sample, or replaceable state. Durable events need persistence and acknowledgement; samples can use a documented drop policy with counters; state can conflate to latest.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A telemetry pipeline drops values under load. How do you decide whether this is a bug?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Backpressure contract:</strong> StateFlow تحتفظ بقيمة حالية وتعمل equality conflation. SharedFlow تبث للقائمين بالcollection حسب replay وbuffer policy. الاتنين in-memory؛ حدث لازم ينجو من process death أويتنفذ once يحتاج storage وidentity وacknowledgement.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBackpressure contract: مثّل durable outcome في state أو storage بهوية وacknowledgement، استخدم StateFlow للstate، وSharedFlow فقط للeffects اللي missed delivery فيها مقبولة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “SharedFlow with replay zero is a reliable event bus for payment or navigation results.”

<p dir="rtl" lang="ar">في <strong>Backpressure contract</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Backpressure contract: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Backpressure contract: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Backpressure contract، الـshortcut هي: <bdi dir="ltr">SharedFlow with replay zero is a reliable event bus for payment or navigation results.</bdi> ودي تكسر: state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Backpressure contract: أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Backpressure contract: Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.</span>

## English model answer

“I classify each value: durable business event, diagnostic sample, or replaceable state. Durable events need persistence and acknowledgement; samples can use a documented drop policy with counters; state can conflate to latest. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
