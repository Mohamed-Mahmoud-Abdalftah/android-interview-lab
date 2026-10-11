---
id: INT-Q011-ANSWER
question_id: INT-Q011
status: reviewed
---
# INT-Q011 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Quantify affected users, functions, versions, geographies, and data/security impact.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A new release causes intermittent checkout failures. Explain how you determine severity using affected users, business function, data integrity, security, and duration.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Severity and scope:</strong> severity تتحدد من عدد المستخدمين والوظائف والdata/security impact، مش صوت أعلى شخص. Incident Commander تنسق timeline والقرارات، وmitigation reversible تقلل الضرر قبل اكتمال root cause. follow-up لا تتقفل إلا بowner وdeadline ودليل.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSeverity and scope: حدد versions/users/data impact، عيّن roles، rollback/flag بأقل blast radius، ثم اختبر hypothesis بالملاحظة الأكثر تمييزًا وسجل follow-ups قابلة للإغلاق.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Wait for the exact root cause before mitigating a high-impact incident.”

<p dir="rtl" lang="ar">في <strong>Severity and scope</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Severity and scope: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Severity and scope: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Severity and scope، الـshortcut هي: <bdi dir="ltr">Wait for the exact root cause before mitigating a high-impact incident.</bdi> ودي تكسر: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Severity and scope: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Severity and scope: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</span>

## English model answer

“Quantify affected users, functions, versions, geographies, and data/security impact. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
