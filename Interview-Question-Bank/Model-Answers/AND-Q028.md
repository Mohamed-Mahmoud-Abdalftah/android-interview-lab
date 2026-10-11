---
id: AND-Q028-ANSWER
question_id: AND-Q028
status: reviewed
---
# AND-Q028 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Choose dimensions that separate hypotheses: fresh versus restored, process alive versus recreated, foreground versus background, and network state. Start pairwise and add only evidence-driven cases.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـdiagnosis تفصل observation عن inference وتربط نفس timestamp والbuild والprocess بالmain stack والowner اللي موقفها.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">How do you keep a lifecycle bug reproduction matrix useful instead of combinatorial?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Reproduction matrix:</strong> الـANR trace snapshot لحظة من timeline. لازم تحدد main thread كانت Running ولا Blocked ولا Waiting، وبعدها تتبع lock owner أوBinder peer وتربط timestamp بـPerfetto وlogcat. أعلى frame في stack ممكن تكون مكان الانتظار وليست سبب الانتظار.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـReproduction matrix: ابدأ بنوع ANR والوقت، صنّف main thread running أو blocked، اتبع Binder/lock owner، وبعدها اختار experiment واحدة تفرق بين أقوى فرضيتين.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The top application frame is the root cause, so no owner or timeline analysis is needed.”

<p dir="rtl" lang="ar">في <strong>Reproduction matrix</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـdiagnosis تفصل observation عن inference وتربط نفس timestamp والbuild والprocess بالmain stack والowner اللي موقفها. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Reproduction matrix: bugreport مفيد للسياق الواسع وdumpsys للsnapshot؛ متستخدمهمش بدل timeline لما السؤال عن latency ordering.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Reproduction matrix: كرر الرحلة على release-like build واجمع ANR trace وPerfetto/logcat correlation؛ النجاح إن نفس trigger لا يتجاوز budget والtrace تزيل سبب الانتظار.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Reproduction matrix، الـshortcut هي: <bdi dir="ltr">The top application frame is the root cause, so no owner or timeline analysis is needed.</bdi> ودي تكسر: الـdiagnosis تفصل observation عن inference وتربط نفس timestamp والbuild والprocess بالmain stack والowner اللي موقفها.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Reproduction matrix: كرر الرحلة على release-like build واجمع ANR trace وPerfetto/logcat correlation؛ النجاح إن نفس trigger لا يتجاوز budget والtrace تزيل سبب الانتظار.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Reproduction matrix: bugreport مفيد للسياق الواسع وdumpsys للsnapshot؛ متستخدمهمش بدل timeline لما السؤال عن latency ordering.</span>

## English model answer

“Choose dimensions that separate hypotheses: fresh versus restored, process alive versus recreated, foreground versus background, and network state. Start pairwise and add only evidence-driven cases. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
