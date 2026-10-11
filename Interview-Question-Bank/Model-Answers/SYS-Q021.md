---
id: SYS-Q021-ANSWER
question_id: SYS-Q021
status: reviewed
---
# SYS-Q021 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A push is a delivery hint; fetch or reconcile canonical data and handle duplicates.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> push/realtime delivery مجرد signal قابلة للتكرار والفقد؛ canonical stream تستخدم cursor/sequence وتكشف gaps، والlocation لها age/accuracy/retention واضحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A product manager says push notifications guarantee the phone has every update. Explain delivery limits and design push as a hint that triggers idempotent catch-up.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Push as signal:</strong> push وWebSocket delivery ممكن تتكرر أوتضيع أوتوصل بترتيب مختلف. client تحفظ آخر server sequence، تكشف gap، تعمل catch-up، وبعدها dedupe قبل apply. connection owner واحدة تمنع sockets متوازية بعد network flap.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـPush as signal: اعمل owner واحدة للconnection، backoff+jitter وcatch-up من cursor، dedupe قبل apply، واعرض freshness مع تقليل location precision والretention.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A WebSocket or push notification guarantees complete, ordered, exactly-once data.”

<p dir="rtl" lang="ar">في <strong>Push as signal</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: push/realtime delivery مجرد signal قابلة للتكرار والفقد؛ canonical stream تستخدم cursor/sequence وتكشف gaps، والlocation لها age/accuracy/retention واضحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Push as signal: push plus periodic fetch أبسط وأوفر battery لو sub-second realtime مش requirement.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Push as signal: احذف وكرر وبدّل ترتيب events، اعمل network flap وtoken expiry، ثم اثبت gap recovery وconnection واحدة وprivacy-safe telemetry.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Push as signal، الـshortcut هي: <bdi dir="ltr">A WebSocket or push notification guarantees complete, ordered, exactly-once data.</bdi> ودي تكسر: push/realtime delivery مجرد signal قابلة للتكرار والفقد؛ canonical stream تستخدم cursor/sequence وتكشف gaps، والlocation لها age/accuracy/retention واضحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Push as signal: احذف وكرر وبدّل ترتيب events، اعمل network flap وtoken expiry، ثم اثبت gap recovery وconnection واحدة وprivacy-safe telemetry.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Push as signal: push plus periodic fetch أبسط وأوفر battery لو sub-second realtime مش requirement.</span>

## English model answer

“A push is a delivery hint; fetch or reconcile canonical data and handle duplicates. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
