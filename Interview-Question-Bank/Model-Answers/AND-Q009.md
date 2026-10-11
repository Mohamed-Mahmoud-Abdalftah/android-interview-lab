---
id: AND-Q009-ANSWER
question_id: AND-Q009
status: reviewed
---
# AND-Q009 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use it for small UI state tied to composition restoration. Hoist screen behavior to a state holder and keep durable business data in the data layer.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">When is rememberSaveable useful and when should state move to a ViewModel or repository?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في rememberSaveable boundary:</strong> وقت configuration change، الـActivity والـView tree بيتعمل لهم recreation، بينما ViewModel الخاصة بالowner القديمة ممكن تتوصل بالowner الجديدة. وقت process death مفيش object بتعيش؛ Android يرجع Bundle صغيرة، والتطبيق يعيد تحميل البيانات باستخدام ID ثابتة من database أوnetwork.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـrememberSaveable boundary: افصل transient UI state عن durable business state، خزّن key صغيرة في SavedStateHandle أو rememberSaveable، وأعد بناء الشاشة من repository بعد process recreation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “ViewModel survives process death, so keeping the whole screen model there is enough.”

<p dir="rtl" lang="ar">في <strong>rememberSaveable boundary</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في rememberSaveable boundary: لو القيمة قابلة لإعادة الاشتقاق متخزنهاش؛ ولو هي user-authored data كبيرة احفظها في durable store بدل Bundle.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار rememberSaveable boundary: غيّر configuration ثم أعد إنشاء الـActivity بsaved state، وبعدها نفّذ fresh process-style launch من غير reuse لأي fake أو singleton وتأكد إن نفس الـID يعيد canonical data.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في rememberSaveable boundary، الـshortcut هي: <bdi dir="ltr">ViewModel survives process death, so keeping the whole screen model there is enough.</bdi> ودي تكسر: الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار rememberSaveable boundary: غيّر configuration ثم أعد إنشاء الـActivity بsaved state، وبعدها نفّذ fresh process-style launch من غير reuse لأي fake أو singleton وتأكد إن نفس الـID يعيد canonical data.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في rememberSaveable boundary: لو القيمة قابلة لإعادة الاشتقاق متخزنهاش؛ ولو هي user-authored data كبيرة احفظها في durable store بدل Bundle.</span>

## English model answer

“Use it for small UI state tied to composition restoration. Hoist screen behavior to a state holder and keep durable business data in the data layer. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
