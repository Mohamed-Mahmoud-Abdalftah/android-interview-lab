---
id: STF-Q009-ANSWER
question_id: STF-Q009
status: reviewed
---
# STF-Q009 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Make trade-offs and evidence visible, decide with an owner, and document dissent without paralysis.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Two teams disagree on a shared API and both have valid constraints. Walk through how you surface invariants, compare options, decide, and record dissent without stalling delivery.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Cross-team disagreement:</strong> قرار Staff-level يتحول من رأي إلى system تشغيل: user outcome وSLO وowner وmigration وrollback وon-call. strangler seam تقلل blast radius، وplatform لا تعتبر ناجحة من غير consumers حقيقية وadoption/support metrics.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCross-team disagreement: حوّل الغموض لـjourneys/SLO/non-goals، ابدأ seam قابلة للرجوع، عيّن decision/operations owners، ووسع بعد adoption وreliability evidence.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A clean rewrite and central platform will solve the problem after every team is forced to migrate.”

<p dir="rtl" lang="ar">في <strong>Cross-team disagreement</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Cross-team disagreement: manual process أوlocal library مؤقتة أفضل لو uncertainty عالية أو عدد consumers لا يبرر platform/migration.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Cross-team disagreement: جرّب consumer حقيقية، fail dependency، نفّذ rollback/cutover rehearsal، وراقب adoption/error budget/cost قبل توسيع النطاق.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Cross-team disagreement، الـshortcut هي: <bdi dir="ltr">A clean rewrite and central platform will solve the problem after every team is forced to migrate.</bdi> ودي تكسر: القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Cross-team disagreement: جرّب consumer حقيقية، fail dependency، نفّذ rollback/cutover rehearsal، وراقب adoption/error budget/cost قبل توسيع النطاق.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Cross-team disagreement: manual process أوlocal library مؤقتة أفضل لو uncertainty عالية أو عدد consumers لا يبرر platform/migration.</span>

## English model answer

“Make trade-offs and evidence visible, decide with an owner, and document dissent without paralysis. I would shape measurable requirements, assign ownership, bound the blast radius, and design migration, rollback, and operations before committing to a broad platform change. I would validate the decision with adoption, reliability, cost, migration, and rollback evidence before expanding its blast radius.”
