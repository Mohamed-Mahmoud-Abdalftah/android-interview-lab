---
id: CON-Q008-ANSWER
question_id: CON-Q008
status: reviewed
---
# CON-Q008 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Bound queues and define suspend, reject, drop, or conflate policy from event semantics.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> سرعة producer والconsumer غير متساوية، لذلك queue لازم تكون bounded وسياسة suspend/drop/conflate/batch تطابق معنى كل event؛ command لا تُعامل كstate snapshot.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A producer emits 10,000 updates per second and the UI can render 60. Choose between buffering, conflation, dropping, batching, and slowing the producer based on value semantics.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Backpressure:</strong> سرعة producer والconsumer غير متساوية، لذلك queue لازم تكون bounded وسياسة suspend/drop/conflate/batch تطابق معنى كل event؛ command لا تُعامل كstate snapshot. حدد capacity وoverflow policy صراحة: conflate للstate التي يهم آخرها، buffer محدود للbursts، batch للtelemetry، وsuspend أوdurable queue للأحداث التي ممنوع تضيع.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBackpressure: حدد capacity وoverflow policy صراحة: conflate للstate التي يهم آخرها، buffer محدود للbursts، batch للtelemetry، وsuspend أوdurable queue للأحداث التي ممنوع تضيع.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Use an unlimited buffer so no event is ever lost.”

<p dir="rtl" lang="ar">في <strong>Backpressure</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: سرعة producer والconsumer غير متساوية، لذلك queue لازم تكون bounded وسياسة suspend/drop/conflate/batch تطابق معنى كل event؛ command لا تُعامل كstate snapshot. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Backpressure: لو producer قابل للتحكم فـbackpressure upstream أفضل من إسقاط downstream؛ durable queue مطلوبة لما الحدث لازم ينجو من process death.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Backpressure: شغّل producer أسرع 100 مرة من consumer، املأ الـbuffer، ألغِ collector، وأثبت بالIDs أي قيم وصلت أواتجمعت أواترفضت وحد الذاكرة الأقصى.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Backpressure، الـshortcut هي: <bdi dir="ltr">Use an unlimited buffer so no event is ever lost.</bdi> ودي تكسر: سرعة producer والconsumer غير متساوية، لذلك queue لازم تكون bounded وسياسة suspend/drop/conflate/batch تطابق معنى كل event؛ command لا تُعامل كstate snapshot.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Backpressure: شغّل producer أسرع 100 مرة من consumer، املأ الـbuffer، ألغِ collector، وأثبت بالIDs أي قيم وصلت أواتجمعت أواترفضت وحد الذاكرة الأقصى.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Backpressure: لو producer قابل للتحكم فـbackpressure upstream أفضل من إسقاط downstream؛ durable queue مطلوبة لما الحدث لازم ينجو من process death.</span>

## English model answer

“Bound queues and define suspend, reject, drop, or conflate policy from event semantics. I would state the shared invariant, demonstrate the harmful interleaving, and choose immutability, confinement, a mutex, or atomic state according to the whole invariant. I would force harmful interleavings, verify atomic state transitions, and cover cancellation while the critical section is active.”
