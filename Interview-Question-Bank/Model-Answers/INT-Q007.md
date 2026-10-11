---
id: INT-Q007-ANSWER
question_id: INT-Q007
status: reviewed
---
# INT-Q007 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use reducer unit tests, persistence migration tests, worker integration, and UI journeys for distinct risks.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل layer تثبت risk مختلفة، operation identity تتبع الرحلة بلا sensitive content، وAndroid claims لا تُنسب لـJVM-only evidence.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A team has 2,000 slow UI tests and few lower-level tests. Rebuild the portfolio around failure risk, feedback speed, framework boundaries, and production evidence.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Test portfolio:</strong> الـcapstone تتبع operation ID واحدة من UI intent إلى local transaction ثم outbox وworker وserver result. كل test layer تمسك risk مختلفة: reducer للstate، database للdurability، worker للretry، وdevice للframework. telemetry تسجل stage وduration من غير content حساس.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTest portfolio: اربط UI intent بـlocal transaction/outbox/session owner، اختبر reducer والمigration/worker/UI عند boundaries منفصلة، وسمّ بوضوح ما تم تنفيذه فعليًا.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “One end-to-end happy path proves every layer and a JVM model counts as Android runtime evidence.”

<p dir="rtl" lang="ar">في <strong>Test portfolio</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل layer تثبت risk مختلفة، operation identity تتبع الرحلة بلا sensitive content، وAndroid claims لا تُنسب لـJVM-only evidence. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Test portfolio: conceptual design مفيدة للتفسير لكنها لا تستبدل device evidence؛ متوسعش test layer أعلى لو unit contract تكفي.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Test portfolio: inject process death/offline/conflict/account switch/duplicate work، وتتبع redacted operation ID من intent حتى reconciliation.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Test portfolio، الـshortcut هي: <bdi dir="ltr">One end-to-end happy path proves every layer and a JVM model counts as Android runtime evidence.</bdi> ودي تكسر: كل layer تثبت risk مختلفة، operation identity تتبع الرحلة بلا sensitive content، وAndroid claims لا تُنسب لـJVM-only evidence.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Test portfolio: inject process death/offline/conflict/account switch/duplicate work، وتتبع redacted operation ID من intent حتى reconciliation.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Test portfolio: conceptual design مفيدة للتفسير لكنها لا تستبدل device evidence؛ متوسعش test layer أعلى لو unit contract تكفي.</span>

## English model answer

“Use reducer unit tests, persistence migration tests, worker integration, and UI journeys for distinct risks. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
