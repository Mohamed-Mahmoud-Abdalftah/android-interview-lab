---
id: SYS-Q020-ANSWER
question_id: SYS-Q020
status: reviewed
---
# SYS-Q020 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Track pending age, retry reason, conflicts, and success without logging note content.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> local canonical state والoutbox تتحدث في transaction، وكل mutation لها ID/version، والdelete تظل tombstone لحد acknowledgement.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Define metrics and logs for an offline sync engine: queue age, attempts, conflicts, freshness, terminal failures, and redaction. Which signal pages an on-call engineer?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Sync observability:</strong> الـUI تقرأ local database كحقيقة حالية. user edit وoutbox operation يتكتبوا في transaction واحدة، والworker ترسل operation ID ثابتة. response ترجع transaction تحدث canonical row وتمسح pending marker؛ version/tombstone تمنع stale overwrite وresurrection.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSync observability: اكتب local change وoutbox atomically، sync idempotently، طبق domain conflict policy، واحتفظ tombstone/dirty metadata لحد server confirmation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Last response wins, and a failed request can be retried without durable identity.”

<p dir="rtl" lang="ar">في <strong>Sync observability</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: local canonical state والoutbox تتحدث في transaction، وكل mutation لها ID/version، والdelete تظل tombstone لحد acknowledgement. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Sync observability: server-first أبسط لو offline غير مطلوبة؛ CRDT أو merge آلي لا يستخدم إلا لما domain semantics تبرره.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Sync observability: اقتل process بعد local commit وقبل send، كرر delivery، أخّر response قديمة، واعمل delete offline؛ اثبت عدم فقد intent أو resurrection.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Sync observability، الـshortcut هي: <bdi dir="ltr">Last response wins, and a failed request can be retried without durable identity.</bdi> ودي تكسر: local canonical state والoutbox تتحدث في transaction، وكل mutation لها ID/version، والdelete تظل tombstone لحد acknowledgement.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Sync observability: اقتل process بعد local commit وقبل send، كرر delivery، أخّر response قديمة، واعمل delete offline؛ اثبت عدم فقد intent أو resurrection.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Sync observability: server-first أبسط لو offline غير مطلوبة؛ CRDT أو merge آلي لا يستخدم إلا لما domain semantics تبرره.</span>

## English model answer

“Track pending age, retry reason, conflicts, and success without logging note content. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
