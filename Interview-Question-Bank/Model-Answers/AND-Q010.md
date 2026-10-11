---
id: AND-Q010-ANSWER
question_id: AND-Q010
status: reviewed
---
# AND-Q010 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Test reducer persistence separately, then Android recreation with saved state, and a fresh process-style launch that reloads durable cart identity without reusing memory fakes.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Design tests for a checkout screen across rotation and process death.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Restoration test design:</strong> وقت configuration change، الـActivity والـView tree بيتعمل لهم recreation، بينما ViewModel الخاصة بالowner القديمة ممكن تتوصل بالowner الجديدة. وقت process death مفيش object بتعيش؛ Android يرجع Bundle صغيرة، والتطبيق يعيد تحميل البيانات باستخدام ID ثابتة من database أوnetwork.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRestoration test design: افصل transient UI state عن durable business state، خزّن key صغيرة في SavedStateHandle أو rememberSaveable، وأعد بناء الشاشة من repository بعد process recreation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “ViewModel survives process death, so keeping the whole screen model there is enough.”

<p dir="rtl" lang="ar">في <strong>Restoration test design</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Restoration test design: لو القيمة قابلة لإعادة الاشتقاق متخزنهاش؛ ولو هي user-authored data كبيرة احفظها في durable store بدل Bundle.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Restoration test design: غيّر configuration ثم أعد إنشاء الـActivity بsaved state، وبعدها نفّذ fresh process-style launch من غير reuse لأي fake أو singleton وتأكد إن نفس الـID يعيد canonical data.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Restoration test design، الـshortcut هي: <bdi dir="ltr">ViewModel survives process death, so keeping the whole screen model there is enough.</bdi> ودي تكسر: الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Restoration test design: غيّر configuration ثم أعد إنشاء الـActivity بsaved state، وبعدها نفّذ fresh process-style launch من غير reuse لأي fake أو singleton وتأكد إن نفس الـID يعيد canonical data.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Restoration test design: لو القيمة قابلة لإعادة الاشتقاق متخزنهاش؛ ولو هي user-authored data كبيرة احفظها في durable store بدل Bundle.</span>

## English model answer

“Test reducer persistence separately, then Android recreation with saved state, and a fresh process-style launch that reloads durable cart identity without reusing memory fakes. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
