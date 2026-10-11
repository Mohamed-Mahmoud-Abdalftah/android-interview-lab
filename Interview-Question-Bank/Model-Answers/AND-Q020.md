---
id: AND-Q020-ANSWER
question_id: AND-Q020
status: reviewed
---
# AND-Q020 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “At the data boundary that knows the driver is blocking, so callers receive a main-safe suspend contract. Do not scatter dispatcher guesses through UI code.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـAPI التي تعرف إن driver blocking هي اللي تضمن main-safety؛ caller لا يفترض dispatcher داخلي غير موثق.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Where should withContext(IO) live for a blocking database driver?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Main-safe API contract:</strong> كلمة suspend لا تختار thread. الـdata source اللي تعرف إن driver blocking هي المسؤولة تنقل الجزء blocking إلى injected IO dispatcher، وبكده كل caller تحصل على main-safe contract من غير ما تعرف implementation.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMain-safe API contract: اعزل blocking driver داخل repository/data source باستخدام dispatcher injected، وخلي الـsuspend contract آمنة لأي caller.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Every suspend function automatically leaves the main thread.”

<p dir="rtl" lang="ar">في <strong>Main-safe API contract</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـAPI التي تعرف إن driver blocking هي اللي تضمن main-safety؛ caller لا يفترض dispatcher داخلي غير موثق. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Main-safe API contract: لو library API async أصلًا، متضيفش withContext بلا قياس لأنه ممكن يضيف hops من غير حماية.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Main-safe API contract: استدعِ الـAPI من Main test dispatcher مع fake blocking boundary وتحقق إن blocking segment اتنفذ على dispatcher المتوقعة وإن cancellation وصلت.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Main-safe API contract، الـshortcut هي: <bdi dir="ltr">Every suspend function automatically leaves the main thread.</bdi> ودي تكسر: الـAPI التي تعرف إن driver blocking هي اللي تضمن main-safety؛ caller لا يفترض dispatcher داخلي غير موثق.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Main-safe API contract: استدعِ الـAPI من Main test dispatcher مع fake blocking boundary وتحقق إن blocking segment اتنفذ على dispatcher المتوقعة وإن cancellation وصلت.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Main-safe API contract: لو library API async أصلًا، متضيفش withContext بلا قياس لأنه ممكن يضيف hops من غير حماية.</span>

## English model answer

“At the data boundary that knows the driver is blocking, so callers receive a main-safe suspend contract. Do not scatter dispatcher guesses through UI code. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
