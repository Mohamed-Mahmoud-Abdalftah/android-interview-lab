---
id: PRO-Q027-ANSWER
question_id: PRO-Q027
status: reviewed
---
# PRO-Q027 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Increase exposure only after a fixed observation window and comparable health metrics.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل release لها blocking gates مستقلة وcohort قابلة للمقارنة وowner وthreshold وrollback action محددين قبل زيادة exposure.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Design a staged rollout with cohort size, observation window, dashboards, owners, and automatic stop conditions. What bias appears if only early adopters receive the release?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Staged rollout:</strong> الـstaged rollout تقسم exposure إلى cohorts وتنتظر observation window ثابتة. crash وdata loss وsecurity كل واحدة gate مستقلة؛ المتوسط لا يلغي blocker. rollback trigger يتحدد قبل الضغط عشان الفريق ما يغيرش threshold أثناء الحادث.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـStaged rollout: ابدأ cohort صغيرة، راقب correctness/security/crash/latency كل واحدة كgate، وقف أو ارجع عند threshold، واحفظ evidence للroot cause.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Average health is acceptable, so one blocking security or data signal can be ignored.”

<p dir="rtl" lang="ar">في <strong>Staged rollout</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل release لها blocking gates مستقلة وcohort قابلة للمقارنة وowner وthreshold وrollback action محددين قبل زيادة exposure. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Staged rollout: weighted score لا يعوض blocker أمني أو data loss؛ manual approval مفيدة فقط مع evidence وowner واضحين.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Staged rollout: اختبر flag/rollback فعليًا، inject failure في staging، وتأكد إن dashboards تفصل version/cohort وإن alert تسبق توسع الـblast radius.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Staged rollout، الـshortcut هي: <bdi dir="ltr">Average health is acceptable, so one blocking security or data signal can be ignored.</bdi> ودي تكسر: كل release لها blocking gates مستقلة وcohort قابلة للمقارنة وowner وthreshold وrollback action محددين قبل زيادة exposure.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Staged rollout: اختبر flag/rollback فعليًا، inject failure في staging، وتأكد إن dashboards تفصل version/cohort وإن alert تسبق توسع الـblast radius.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Staged rollout: weighted score لا يعوض blocker أمني أو data loss؛ manual approval مفيدة فقط مع evidence وowner واضحين.</span>

## English model answer

“Increase exposure only after a fixed observation window and comparable health metrics. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
