---
id: STF-Q004-ANSWER
question_id: STF-Q004
status: reviewed
---
# STF-Q004 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Tie reliability targets to user outcomes and use budget to balance change velocity and risk.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Choose an SLO for a mobile sync journey, define good and bad events, and explain how an error budget changes release decisions.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في SLO and error budget:</strong> قرار Staff-level يتحول من رأي إلى system تشغيل: user outcome وSLO وowner وmigration وrollback وon-call. strangler seam تقلل blast radius، وplatform لا تعتبر ناجحة من غير consumers حقيقية وadoption/support metrics.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSLO and error budget: حوّل الغموض لـjourneys/SLO/non-goals، ابدأ seam قابلة للرجوع، عيّن decision/operations owners، ووسع بعد adoption وreliability evidence.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A clean rewrite and central platform will solve the problem after every team is forced to migrate.”

<p dir="rtl" lang="ar">في <strong>SLO and error budget</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في SLO and error budget: manual process أوlocal library مؤقتة أفضل لو uncertainty عالية أو عدد consumers لا يبرر platform/migration.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار SLO and error budget: جرّب consumer حقيقية، fail dependency، نفّذ rollback/cutover rehearsal، وراقب adoption/error budget/cost قبل توسيع النطاق.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في SLO and error budget، الـshortcut هي: <bdi dir="ltr">A clean rewrite and central platform will solve the problem after every team is forced to migrate.</bdi> ودي تكسر: القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار SLO and error budget: جرّب consumer حقيقية، fail dependency، نفّذ rollback/cutover rehearsal، وراقب adoption/error budget/cost قبل توسيع النطاق.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في SLO and error budget: manual process أوlocal library مؤقتة أفضل لو uncertainty عالية أو عدد consumers لا يبرر platform/migration.</span>

## English model answer

“Tie reliability targets to user outcomes and use budget to balance change velocity and risk. I would shape measurable requirements, assign ownership, bound the blast radius, and design migration, rollback, and operations before committing to a broad platform change. I would validate the decision with adoption, reliability, cost, migration, and rollback evidence before expanding its blast radius.”
