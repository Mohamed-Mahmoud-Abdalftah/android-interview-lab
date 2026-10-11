---
id: SYS-Q012-ANSWER
question_id: SYS-Q012
status: reviewed
---
# SYS-Q012 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A refresh result is accepted only for the current account generation and cannot revive a logged-out session.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> session transition تخص account generation الحالية، logout لا يمكن أن تُعكسها refresh قديمة، والbackend هو authority للauthorization.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A token refresh starts, the user logs out, and the refresh succeeds later. Trace the race and show how an account generation or session ID prevents stale commit.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Refresh race:</strong> session state machine تربط كل token وcache وwork بـaccount generation. لو refresh بدأت في generation 4 ثم logout نقل الحالة لـ5، نتيجة 4 تُرفض. Keystore تحمي key material على الجهاز لكن server تظل authority للauthorization وrevocation.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRefresh race: نمذج session كstate machine، اربط token/result بـaccount generation، partition cache/work بالaccount ID، وخزن key material عبر Keystore من غير اعتبار client trusted.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A token stored with Keystore makes the client the final authorization authority.”

<p dir="rtl" lang="ar">في <strong>Refresh race</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: session transition تخص account generation الحالية، logout لا يمكن أن تُعكسها refresh قديمة، والbackend هو authority للauthorization. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Refresh race: encrypted local storage تقلل exposure على الجهاز لكنها لا تلغي server revocation ولا تقلل البيانات تلقائيًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Refresh race: ابدأ refresh ثم logout/login لحساب آخر، أكمل refresh القديمة، واستدعِ revoked endpoint؛ اثبت عدم إحياء الجلسة أو اختلاط rows/work.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Refresh race، الـshortcut هي: <bdi dir="ltr">A token stored with Keystore makes the client the final authorization authority.</bdi> ودي تكسر: session transition تخص account generation الحالية، logout لا يمكن أن تُعكسها refresh قديمة، والbackend هو authority للauthorization.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Refresh race: ابدأ refresh ثم logout/login لحساب آخر، أكمل refresh القديمة، واستدعِ revoked endpoint؛ اثبت عدم إحياء الجلسة أو اختلاط rows/work.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Refresh race: encrypted local storage تقلل exposure على الجهاز لكنها لا تلغي server revocation ولا تقلل البيانات تلقائيًا.</span>

## English model answer

“A refresh result is accepted only for the current account generation and cannot revive a logged-out session. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
