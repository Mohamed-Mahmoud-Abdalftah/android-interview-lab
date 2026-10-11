---
id: INT-Q012-ANSWER
question_id: INT-Q012
status: reviewed
---
# INT-Q012 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use a reversible rollback or flag when impact is material, while preserving evidence for diagnosis.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Users are losing work but the root cause is unclear. Choose a reversible mitigation now, preserve evidence, and explain which actions must wait for stronger confidence.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Mitigation before certainty:</strong> severity تتحدد من عدد المستخدمين والوظائف والdata/security impact، مش صوت أعلى شخص. Incident Commander تنسق timeline والقرارات، وmitigation reversible تقلل الضرر قبل اكتمال root cause. follow-up لا تتقفل إلا بowner وdeadline ودليل.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMitigation before certainty: حدد versions/users/data impact، عيّن roles، rollback/flag بأقل blast radius، ثم اختبر hypothesis بالملاحظة الأكثر تمييزًا وسجل follow-ups قابلة للإغلاق.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Wait for the exact root cause before mitigating a high-impact incident.”

<p dir="rtl" lang="ar">في <strong>Mitigation before certainty</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Mitigation before certainty: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Mitigation before certainty: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Mitigation before certainty، الـshortcut هي: <bdi dir="ltr">Wait for the exact root cause before mitigating a high-impact incident.</bdi> ودي تكسر: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Mitigation before certainty: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Mitigation before certainty: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</span>

## English model answer

“Use a reversible rollback or flag when impact is material, while preserving evidence for diagnosis. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
